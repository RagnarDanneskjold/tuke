// ### BOILERPLATE ###
// Tuke - Electrical Design Automation toolset
// Copyright (C) 2008 Peter Todd <pete@petertodd.org>
// 
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.
// ### BOILERPLATE ###

#include <Python.h>
#include "structmember.h"

#include "wrapper.h"
#include "wrap_tuple.h"

PyTypeObject ContextProviderType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "wrapper._ContextProvider",             /*tp_name*/
    sizeof(Wrappable),         /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    0,                         /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "Mixin to signify that an object can provide context.\n\n\
Element should have this as a base class.", /* tp_doc */
};

PyTypeObject WrappableType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "wrapper.Wrappable",             /*tp_name*/
    sizeof(Wrappable),         /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    0,                         /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "Mixin to signify objects that can be wrapped in contexts.", /* tp_doc */
};

PyTypeObject TranslatableType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "wrapper.Translatable",             /*tp_name*/
    sizeof(Translatable),         /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    0,                         /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "Mixin to signify objects that support the (add|remove)_context protocol.", /* tp_doc */
};

PyDictObject *wrapped_cache;

static int
Wrapped_traverse(Wrapped *self, visitproc visit, void *arg){
    Py_VISIT(self->_wrapped_obj);
    Py_VISIT(self->_wrapping_context);
    return 0;
}

static int
Wrapped_clear(Wrapped *self){
    Py_CLEAR(self->_wrapped_obj);
    Py_CLEAR(self->_wrapping_context);
    return 0;
}

static void
Wrapped_dealloc(Wrapped* self){
    PyTupleObject *key;
    if (self->in_weakreflist != NULL)
            PyObject_ClearWeakRefs((PyObject *) self);

    printf("deallocing Wrapped %d %d\n",self->_wrapped_obj,self->_wrapping_context);
    key = (PyTupleObject *)Py_BuildValue("(l,l,i)",
                                         (long)self->_wrapped_obj,
                                         (long)self->_wrapping_context,
                                         self->apply);
    PyDict_DelItem(wrapped_cache,key);

    Py_XDECREF(key);

    Wrapped_clear(self);
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
Wrapped_new(PyTypeObject *type, PyObject *obj, PyObject *context, int apply){
    Wrapped *self;

    self = (Wrapped *)type->tp_alloc(type, 0);
    self->in_weakreflist = NULL;

    self->apply = apply;

    Py_INCREF(obj);
    self->_wrapped_obj = obj;

    Py_INCREF(context);
    self->_wrapping_context = context;

    printf("new Wrapped %d %d %d\n",self->_wrapped_obj,self->_wrapping_context,self->apply);
    return (PyObject *)self;
}

PyObject *
apply_remove_context(PyObject *context,PyObject *obj,int raw_apply){
    PyObject *self,*self_ref;
    int apply = raw_apply ? 1 : 0;

    if (!PyObject_IsInstance(context,&ContextProviderType)){
        PyErr_Format(PyExc_TypeError,
                     "context object must be an Element instance (not \"%.200s\")",
                     context->ob_type->tp_name);
        return NULL;
    }

    // Basic types don't get wrapped at all.
    if (obj == Py_None ||
        PyBool_Check(obj) ||
        PyInt_Check(obj) ||
        PyLong_Check(obj) ||
        PyFloat_Check(obj) || 
        PyComplex_Check(obj) ||
        PyType_Check(obj) ||
        PyString_Check(obj) ||
        PyUnicode_Check(obj) ||
        PyFile_Check(obj)){

        Py_INCREF(obj);
        return obj;
    }
    else if (PyTuple_Check(obj)){
        printf("wrap_tuple (%s,%s)\n",PyString_AsString(PyObject_Repr(context)),
                                 PyString_AsString(PyObject_Repr(obj)));
        return wrap_tuple(context,obj,apply);
    }
    // Translatable types have their context applied, but they can't be put in
    // the cache because they don't have a destructor that would remove them.
    else if (PyObject_IsInstance(obj,(PyObject *)&TranslatableType)){
        printf("trans\n");
        if (apply){
            return PyObject_CallMethod(obj,"_apply_context","O",context);
        } else {
            return PyObject_CallMethod(obj,"_remove_context","O",context);
        }
    }
    else if (!apply && PyObject_IsInstance(obj,(PyObject *)&WrappedType) &&
             ((Wrapped *)obj)->_wrapping_context == context){
        Py_INCREF(((Wrapped *)obj)->_wrapped_obj);
        return ((Wrapped *)obj)->_wrapped_obj;
    }
    // Everything else gets wrapped with some sort of wrapping object.
    else{
        // Return an existing Wrapped object if possible.
        PyTupleObject *key;
     
        // The cache is a dict of (id(obj),id(context),apply) -> Wrapped object.
        //
        // However, an actual reference to Wrapped would cause problems, as it
        // would prevent garbage collection, so instead an opaque PyCObject is
        // used. This is ok, as the Wrapped object itself serves as a
        // reference, so the dict entry will always be deleted before the
        // pointed too object. 
        key = (PyTupleObject *)Py_BuildValue("(l,l,i)",(long)obj,(long)context,apply);
        if (!key) return NULL;
        
        printf("looking for\n");
        self = (Wrapped *)PyDict_GetItem((PyObject *)wrapped_cache,(PyObject *)key);
        printf("self was ");
        if (self){
            self = PyCObject_AsVoidPtr(self);
            Py_INCREF(self);
            Py_DECREF(key);
            return self;
        } else {
            printf("didn't find\n");

            self = Wrapped_new(&WrappedType,obj,context,apply);
            if (!self){
                Py_DECREF(key);
                return NULL;
            }

            PyObject *selfptr;
            selfptr = PyCObject_FromVoidPtr(self,NULL);
            if (!selfptr){
                Py_DECREF(key);
                printf("set item error\n");
                return NULL;
            }

            if (PyDict_SetItem(wrapped_cache,key,selfptr)){
                Py_DECREF(key);
                Py_DECREF(selfptr);
                return NULL;
            }

            Py_DECREF(key);
            Py_DECREF(selfptr);
            return self;
        }
    }
}

PyObject *
wrap(PyTypeObject *junk, PyObject *args){
    PyObject *obj,*context;

    if (!PyArg_ParseTuple(args, "OO", &obj, &context))
        return NULL; 

    return apply_remove_context(context,obj,1);
}


#define xapply_context(self,context,obj) apply_remove_context(context,obj,((Wrapped *)self)->apply) 
#define xremove_context(self,context,obj) apply_remove_context(context,obj,~(((Wrapped *)self)->apply))

#define null_xapply_context(self,context,obj) obj
#define null_xremove_context(self,context,obj) obj

#define WRAP_UNARY(method, generic, apply) \
    static PyObject * \
    method(PyObject *self) { \
        printf("WRAP_UNARY " # method " " # generic " " # apply "\n"); \
        return apply(self,((Wrapped *)self)->_wrapping_context, \
                     generic(((Wrapped *)self)->_wrapped_obj)); \
    }

#define WRAP_BINARY(method, generic, apply, remove) \
    static PyObject * \
    method(PyObject *self, PyObject *args) { \
        printf("WRAP_BINARY " # method " " # generic " " # apply " " # remove "\n"); \
        return apply(self,((Wrapped *)self)->_wrapping_context, \
                     generic(((Wrapped *)self)->_wrapped_obj, \
                             remove(self,((Wrapped *)self)->_wrapping_context,args))); \
    }

#define WRAP_TERNARY(method, generic, apply, remove) \
    static PyObject * \
    method(PyObject *self, PyObject *args, PyObject *kwargs) { \
        printf("WRAP_TERNARY " # method " " # generic " " # apply " " # remove "\n"); \
        return apply(self,((Wrapped *)self)->_wrapping_context, \
                     generic(((Wrapped *)self)->_wrapped_obj, \
                             remove(self,((Wrapped *)self)->_wrapping_context,args), \
                             remove(self,((Wrapped *)self)->_wrapping_context,kwargs))); \
    }


static PyObject *
Wrapped_getattr(Wrapped *self,PyObject *name){
    PyObject *r = NULL;
    printf("getattr %s %s ",PyString_AsString(PyObject_Repr(self)),PyString_AsString(PyObject_Repr(name)));

    r = PyObject_GetAttr(self->_wrapped_obj,name);
    if (r == NULL){
        printf("failed!\n");
        return NULL;
    }

    printf("returning %s\n",PyString_AsString(PyObject_Repr(r)));
    return xapply_context(self,self->_wrapping_context,r);
}

int
Wrapped_setattr(Wrapped *self,PyObject *name,PyObject *value){
    PyObject *unwrapped=NULL;
    int r;

    Py_INCREF(value);
    unwrapped = xremove_context(self,self->_wrapping_context,value);
    Py_INCREF(unwrapped);
    r = PyObject_SetAttr(self->_wrapped_obj,name,unwrapped);
    Py_DECREF(value);

    return r;
}

static PyObject *
Wrapped_call(Wrapped *self,PyObject *args,PyObject *kwargs){
    int i;
    PyObject *unwrapped_args=NULL, *unwrapped_kwargs=NULL;
    PyObject *r,*wr;

    printf("call %s(%s,%s)\n",PyString_AsString(PyObject_Repr(self)),
                             PyString_AsString(PyObject_Repr(args)),
                             PyString_AsString(PyObject_Repr(kwargs)));

    // A straight xremove_context won't work as PyObject_call only handles
    // actual tuple's and dicts for args,kwargs Fortunately *args cannot be
    // assigned to, and assigning to **kwargs doesn't change the callers
    // **kwargs, otherwise we'd have an unhandled edge case for those expat
    // C++-programmers.

    // Pretty sure this can only be called in wrapped mode, so insure that
    // assumption is correct.
    if (self->apply != 1){
        PyErr_SetString(PyExc_RuntimeError,"Wrapped_call while self->apply != 1");
        return NULL;
    }

    Py_XINCREF(args);
    unwrapped_args = PyTuple_New(PyTuple_GET_SIZE(args));
    if (unwrapped_args == NULL) return NULL;
    for (i = 0; i < PyTuple_GET_SIZE(args); i++){
        PyObject *v = PyTuple_GET_ITEM(args,i),*w = NULL;

        w = xremove_context(self,self->_wrapping_context,v);
        PyTuple_SET_ITEM(unwrapped_args,i,w);
    }

    if (kwargs != NULL){
        Py_XINCREF(kwargs);
        unwrapped_kwargs = PyDict_New();
        if (!unwrapped_kwargs) return NULL;
        PyObject *k,*v;
        Py_ssize_t pos = 0;
        while (PyDict_Next(kwargs,&pos,&k,&v)){
            v = xremove_context(self,self->_wrapping_context,v);
            if (PyDict_SetItem(unwrapped_kwargs,k,v)) return NULL;
            Py_DECREF(v);
        }
    }

    printf("unwcall %s(%s,%s)\n",PyString_AsString(PyObject_Repr(self)),
                             PyString_AsString(PyObject_Repr(unwrapped_args)),
                             PyString_AsString(PyObject_Repr(unwrapped_kwargs)));
    r = PyObject_Call(self->_wrapped_obj,unwrapped_args,unwrapped_kwargs);
    // Currently calling a un-callable Wrapped object gets to this point, but
    // with an exception, so the following DECREF's are important and may see
    // user code.
    Py_DECREF(unwrapped_args);
    Py_XDECREF(unwrapped_kwargs);
    if (r == NULL) return NULL;

    printf("returning %s\n",PyString_AsString(PyObject_Repr(r)));
    wr = xapply_context(self,self->_wrapping_context,r);
    Py_DECREF(r);

    printf("returning %s\n",PyString_AsString(PyObject_Repr(wr)));

    return wr;
}

WRAP_UNARY(Wrapped_str, PyObject_Str,null_xapply_context)

WRAP_BINARY(Wrapped_compare,PyObject_Compare,null_xapply_context,xremove_context)

static PyObject *
Wrapped_repr(Wrapped *self){
    char buf[360];
    PyOS_snprintf(buf,sizeof(buf),
                  "<Wrapped at %p wrapping %.100s at %p with %.100s at %p>", self,
                  self->_wrapped_obj->ob_type->tp_name,
                  self->_wrapped_obj,
                  self->_wrapping_context->ob_type->tp_name,
                  self->_wrapping_context);
    return PyString_FromString(buf);
}

static PyMemberDef Wrapped_members[] = {
    {"_wrapped_obj", T_OBJECT_EX, offsetof(Wrapped, _wrapped_obj), 0,
     "_wrapped_obj name"},
    {"_wrapping_context", T_OBJECT_EX, offsetof(Wrapped, _wrapping_context), 0,
     "_wrapping_context name"},
    {NULL}  /* Sentinel */
};

PyTypeObject WrappedType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "wrapper.Wrapped",             /*tp_name*/
    sizeof(Wrapped),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)Wrapped_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    Wrapped_compare,           /*tp_compare*/
    Wrapped_repr,              /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    Wrapped_call,              /*tp_call*/
    Wrapped_str,               /*tp_str*/
    Wrapped_getattr,           /*tp_getattro*/
    Wrapped_setattr,           /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC, /*tp_flags*/
    "Wrap object in a context",           /* tp_doc */
    (traverseproc)Wrapped_traverse,     /* tp_traverse */
    (inquiry)Wrapped_clear,             /* tp_clear */
    0,		               /* tp_richcompare */
    offsetof(Wrapped, in_weakreflist),  /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    0,             /* tp_methods */
    Wrapped_members,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    0,      /* tp_init */
    0,                         /* tp_alloc */
    0,                         /* tp_new */
};

static PyMethodDef methods[] = {
    {"wrap", (PyCFunction)wrap, METH_VARARGS,
     "Wrap an object."},
    {NULL,NULL,0,NULL}
};

#ifndef PyMODINIT_FUNC	// declarations for DLL import/export
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initwrapper(void) 
{
    PyObject* m;

    wrapped_cache = PyDict_New();
    if (!wrapped_cache)
        return;

    if (PyType_Ready(&WrappedType) < 0)
        return;

    ContextProviderType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&ContextProviderType) < 0)
        return;

    WrappableType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&WrappableType) < 0)
        return;

    TranslatableType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&TranslatableType) < 0)
        return;

    m = Py_InitModule3("wrapper", methods,
                       "Object wrapping");
    if (m == NULL)
        return;

    Py_INCREF(&WrappedType);
    PyModule_AddObject(m, "Wrapped", (PyObject *)&WrappedType);
    PyModule_AddObject(m, "_ContextProvider", (PyObject *)&ContextProviderType);
    PyModule_AddObject(m, "Wrappable", (PyObject *)&WrappableType);
    PyModule_AddObject(m, "Translatable", (PyObject *)&TranslatableType);
    PyModule_AddObject(m, "_wrapped_cache",(PyObject *)wrapped_cache);
}

// Local Variables:
// mode: C
// fill-column: 76
// c-file-style: "gnu"
// indent-tabs-mode: nil
// End:
// vim: et:sw=4:sts=4:ts=4:cino=>4s,{s,\:s,+s,t0,g0,^-4,e-4,n-4,p4s,(0,=s:
