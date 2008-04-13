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

typedef struct {
    PyObject_HEAD
} Wrappable;

static PyTypeObject WrappableType = {
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

typedef struct {
    PyObject_HEAD
} Translatable;

static PyTypeObject TranslatableType = {
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

static PyTypeObject WrappedType;

typedef struct {
    PyObject_HEAD
    PyObject *_wrapped_obj;
    PyObject *_wrapping_context;
    PyObject *in_weakreflist;
} Wrapped;

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

    key = (PyTupleObject *)Py_BuildValue("(l,l)",
                                         (long)self->_wrapped_obj,
                                         (long)self->_wrapping_context);
    PyDict_DelItem(wrapped_cache,key);

    Py_XDECREF(key);

    Wrapped_clear(self);
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
Wrapped_new(PyTypeObject *type, PyObject *obj, PyObject *context)
{
    Wrapped *self;

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

        // If this incref is removed, segfaults happen.
        Py_INCREF(obj);
        return obj;
    }
    else{
        // Return an existing Wrapped object if possible.
        PyTupleObject *key;
     
        // The cache is just a (id(obj),id(context) -> weakref(Wrapped) dict.
        key = (PyTupleObject *)Py_BuildValue("(l,l)",(long)obj,(long)context);
        if (!key) return;
        
        self = (Wrapped *)PyDict_GetItem((PyObject *)wrapped_cache,(PyObject *)key);
        if (self){
            self = PyWeakref_GET_OBJECT(self);
            Py_DECREF(key);
            return self;
        } else {
            self = (Wrapped *)type->tp_alloc(type, 0);

            self->in_weakreflist = NULL;

            Py_INCREF(obj);
            self->_wrapped_obj = obj;

            Py_INCREF(context);
            self->_wrapping_context = context;

            if (PyDict_SetItem(wrapped_cache,key,
                               PyWeakref_NewRef((PyObject *)self,NULL))){
                Py_DECREF(key);
                return NULL;
            }

            Py_DECREF(key);
            return (PyObject *)self;
        }
    }
}

static PyObject *
pyWrapped_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *obj,*context;
    if (! PyArg_ParseTuple(args, "OO", &obj, &context))
        return NULL; 

    return Wrapped_new(type,obj,context);
}

static PyObject *
apply_context(PyObject *context,PyObject *obj){
    PyObject *r;
    printf("apply %s\n",PyString_AsString(PyObject_Repr(context)));
    if (obj == NULL){
        printf("NULL\n");
        return NULL;
    }
    else if (PyType_Check(obj)){
        printf("type\n");
        r = obj;
    }
    else if (PyObject_IsInstance(obj,(PyObject *)&TranslatableType)){
       printf("trans\n");
       r = PyObject_CallMethod(obj,"_apply_context","O",context);
    }
    else if (PyObject_IsInstance(obj,(PyObject *)&WrappableType)){
        printf("wrapp\n");
        r = Wrapped_new(&WrappedType,obj,context);
    }
    else if (PyMethod_Check(obj)){
        printf("method %s\n",PyString_AsString(PyObject_Repr(obj)));
        r = Wrapped_new(&WrappedType,obj,context); 
    }
    else if (PyTuple_CheckExact(obj)){
        printf("tuple %s\n",PyString_AsString(PyObject_Repr(obj)));
        r = PyTuple_New(PyTuple_GET_SIZE(obj));
        if (r == NULL) return NULL;
        int i;
        printf("building tuple\n");
        for (i = 0; i < PyTuple_GET_SIZE(obj); i++){
            PyObject *v = PyTuple_GET_ITEM(obj,i),*w = NULL;

            printf("%s -> ",PyString_AsString(PyObject_Repr(v)));
 
            Py_INCREF(v);
            w = apply_context(context,v);
            printf("%s\n",PyString_AsString(PyObject_Repr(w)));
            if (w != NULL){
                Py_INCREF(w);
                Py_DECREF(v);
                PyTuple_SET_ITEM(r,i,w);
            } else {
                Py_DECREF(v);
                Py_DECREF(r);
                return NULL;
            }
        }
        printf("final tuple -> %s\n",PyString_AsString(PyObject_Repr(r)));
    }
    else if (PyList_CheckExact(obj)){
        printf("tuple %s\n",PyString_AsString(PyObject_Repr(obj)));
        r = PyList_New(PyList_GET_SIZE(obj));
        if (r == NULL) return NULL;
        int i;
        printf("building tuple\n");
        for (i = 0; i < PyList_GET_SIZE(obj); i++){
            PyObject *v = PyList_GET_ITEM(obj,i),*w = NULL;

            printf("%s -> ",PyString_AsString(PyObject_Repr(v)));
 
            Py_INCREF(v);
            w = apply_context(context,v);
            printf("%s\n",PyString_AsString(PyObject_Repr(w)));
            if (w != NULL){
                Py_INCREF(w);
                Py_DECREF(v);
                PyList_SET_ITEM(r,i,w);
            } else {
                Py_DECREF(v);
                Py_DECREF(r);
                return NULL;
            }
        }
        printf("final tuple -> %s\n",PyString_AsString(PyObject_Repr(r)));
    }
    else{
        printf("other %s\n",PyString_AsString(PyObject_Repr(obj)));
        r = obj;
    }
    return r;
}
#define null_apply_context(context,obj) obj

static PyObject *
remove_context(PyObject *context,PyObject *obj){
    PyObject *r;
    printf("remove %s\n",PyString_AsString(PyObject_Repr(context)));
    if (obj == NULL){
        printf("NULL\n");
        return NULL;
    }
    else if (PyType_Check(obj)){
        printf("type\n");
        r = obj;
    }
    else if (PyObject_IsInstance(obj,(PyObject *)&TranslatableType)){
       printf("trans\n");
       r = PyObject_CallMethod(obj,"_remove_context","O",context);
    }
    else if (PyObject_IsInstance(obj,(PyObject *)&WrappableType)){
        printf("wrapp\n");
        r = Wrapped_new(&WrappedType,obj,context);
    }
    else if (PyTuple_CheckExact(obj)){
        printf("tuple %s\n",PyString_AsString(PyObject_Repr(obj)));
        r = PyTuple_New(PyTuple_GET_SIZE(obj));
        if (r == NULL) return NULL;
        int i;
        printf("building tuple\n");
        for (i = 0; i < PyTuple_GET_SIZE(obj); i++){
            PyObject *v = PyTuple_GET_ITEM(obj,i),*w = NULL;

            printf("%s -> ",PyString_AsString(PyObject_Repr(v)));
 
            Py_INCREF(v);
            w = remove_context(context,v);
            printf("%s\n",PyString_AsString(PyObject_Repr(w)));
            if (w != NULL){
                Py_INCREF(w);
                Py_DECREF(v);
                PyTuple_SET_ITEM(r,i,w);
            } else {
                Py_DECREF(v);
                Py_DECREF(r);
                return NULL;
            }
        }
        printf("final tuple -> %s\n",PyString_AsString(PyObject_Repr(r)));
    }
    else if (PyList_CheckExact(obj)){
        printf("tuple %s\n",PyString_AsString(PyObject_Repr(obj)));
        r = PyList_New(PyList_GET_SIZE(obj));
        if (r == NULL) return NULL;
        int i;
        printf("building tuple\n");
        for (i = 0; i < PyList_GET_SIZE(obj); i++){
            PyObject *v = PyList_GET_ITEM(obj,i),*w = NULL;

            printf("%s -> ",PyString_AsString(PyObject_Repr(v)));
 
            Py_INCREF(v);
            w = remove_context(context,v);
            printf("%s\n",PyString_AsString(PyObject_Repr(w)));
            if (w != NULL){
                Py_INCREF(w);
                Py_DECREF(v);
                PyList_SET_ITEM(r,i,w);
            } else {
                Py_DECREF(v);
                Py_DECREF(r);
                return NULL;
            }
        }
        printf("final tuple -> %s\n",PyString_AsString(PyObject_Repr(r)));
    }
    else{
        printf("other %s\n",PyString_AsString(PyObject_Repr(obj)));
        r = obj;
    }
    return r;
}
#define null_remove_context(context,obj) obj

#define WRAP_UNARY(method, generic, apply) \
    static PyObject * \
    method(PyObject *self) { \
        printf("WRAP_UNARY " # method " " # generic " " # apply "\n"); \
        return apply(((Wrapped *)self)->_wrapping_context, \
                     generic(((Wrapped *)self)->_wrapped_obj)); \
    }

#define WRAP_BINARY(method, generic, apply, remove) \
    static PyObject * \
    method(PyObject *self, PyObject *args) { \
        printf("WRAP_BINARY " # method " " # generic " " # apply " " # remove "\n"); \
        return apply(((Wrapped *)self)->_wrapping_context, \
                     generic(((Wrapped *)self)->_wrapped_obj, \
                             remove(((Wrapped *)self)->_wrapping_context,args))); \
    }

#define WRAP_TERNARY(method, generic, apply, remove) \
    static PyObject * \
    method(PyObject *self, PyObject *args, PyObject *kwargs) { \
        printf("WRAP_TERNARY " # method " " # generic " " # apply " " # remove "\n"); \
        return apply(((Wrapped *)self)->_wrapping_context, \
                     generic(((Wrapped *)self)->_wrapped_obj, \
                             remove(((Wrapped *)self)->_wrapping_context,args), \
                             remove(((Wrapped *)self)->_wrapping_context,kwargs))); \
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
    return apply_context(self->_wrapping_context,r);
}

int
Wrapped_setattr(Wrapped *self,PyObject *name,PyObject *value){
    PyObject *unwrapped=NULL;
    int r;

    Py_INCREF(value);
    unwrapped = remove_context(self->_wrapping_context,value);
    Py_INCREF(unwrapped);
    r = PyObject_SetAttr(self->_wrapped_obj,name,unwrapped);
    Py_DECREF(value);

    return r;
}

static PyObject *
Wrapped_call(Wrapped *self,PyObject *args,PyObject *kwargs){
    PyObject *unwrapped_args=NULL, *unwrapped_kwargs=NULL;
    PyObject *r = NULL;

    printf("call %s %s %s\n",PyString_AsString(PyObject_Repr(self)),
                             PyString_AsString(PyObject_Repr(args)),
                             PyString_AsString(PyObject_Repr(kwargs)));

    Py_XINCREF(args);
    unwrapped_args = remove_context(self->_wrapping_context,args);
    if (unwrapped_args == NULL) goto error;
    Py_XINCREF(unwrapped_args);

    if (kwargs != NULL){
        Py_XINCREF(kwargs);
        unwrapped_kwargs = remove_context(self->_wrapping_context,kwargs);
        if (unwrapped_kwargs == NULL) goto error;
        Py_XINCREF(unwrapped_kwargs);
    }

    r = PyObject_Call(self->_wrapped_obj,unwrapped_args,unwrapped_kwargs);

    if (r == NULL) goto error;

    printf("returning %s\n",PyString_AsString(PyObject_Repr(r)));
    r = apply_context(self->_wrapping_context,r);

    printf("returning %s\n",PyString_AsString(PyObject_Repr(r)));

error:
    Py_XDECREF(args);
    Py_XDECREF(kwargs);

    return r;
}

WRAP_UNARY(Wrapped_str, PyObject_Str,null_apply_context)

WRAP_BINARY(Wrapped_compare,PyObject_Compare,null_apply_context,remove_context)

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

static PyTypeObject WrappedType = {
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
    pyWrapped_new,             /* tp_new */
};

static PyMethodDef methods[] = {
    {NULL}
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
