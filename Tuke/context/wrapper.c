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

// Portions of this file are derived from weakrefobject.c from Python2.5 as
// well as _zope_proxy_proxy.c from zope.proxy-3.4.0

#include <Python.h>
#include "structmember.h"

#include "wrapper.h"

#include "wrap_dict.h"
#include "wrap_list.h"
#include "wrap_tuple.h"

#include "source.h"

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

PyObject *wrapped_cache;

static int
Wrapped_traverse(Wrapped *self, visitproc visit, void *arg){
    Py_VISIT(self->wrapped_obj);
    Py_VISIT(self->wrapping_context);
    return 0;
}

static int
Wrapped_clear(Wrapped *self){
    Py_CLEAR(self->wrapped_obj);
    Py_CLEAR(self->wrapping_context);
    return 0;
}

static void
Wrapped_dealloc(Wrapped* self){
    PyObject_GC_UnTrack(self);

    // dealloc can be called with exceptions set, and the dict stuff we do
    // below does not like that.
    PyObject *ptype,*pvalue,*ptraceback;
    PyErr_Fetch(&ptype,&pvalue,&ptraceback);

    PyTupleObject *key;
    if (self->in_weakreflist != NULL)
            PyObject_ClearWeakRefs((PyObject *) self);

    key = (PyTupleObject *)Py_BuildValue("(l,l,i)",
                                         (long)self->wrapped_obj,
                                         (long)self->wrapping_context,
                                         self->apply);
    int r = PyDict_DelItem(wrapped_cache,(PyObject *)key);

    Py_XDECREF(key);

    Wrapped_clear(self);
    PyObject_GC_Del(self);
    PyErr_Restore(ptype,pvalue,ptraceback);
}

static PyObject *
Wrapped_new(PyTypeObject *type, PyObject *obj, PyObject *context, int apply){
    Wrapped *self;

    self = PyObject_GC_New(Wrapped,&WrappedType);
    self->in_weakreflist = NULL;

    self->apply = apply;

    Py_INCREF(obj);
    self->wrapped_obj = obj;

    Py_INCREF(context);
    self->wrapping_context = context;

    PyObject_GC_Track(self);
    return (PyObject *)self;
}

PyObject *
apply_remove_context(PyObject *context,PyObject *obj,int apply){
    PyObject *self;

    if (!obj) return NULL;

    if (!context){
        PyErr_BadInternalCall();
        return NULL;
    }

    if (!PyObject_IsInstance((PyObject *)context,(PyObject *)&SourceType)){
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
        return wrap_tuple(context,obj,apply);
    }
    else if (PyList_Check(obj)){
        return wrap_list(context,obj,apply);
    }
    else if (PyDict_Check(obj)){
        return wrap_dict(context,obj,apply);
    }
    // Slices seem to act strangely when wrapped. Notably they seem to cause
    // "RuntimeWarning: tp_compare didn't return -1 or -2 for exception"
    // errors. Given that slice(Id('a'),Id('b')) is a *very* advanced usage,
    // best to simply ignore this case for now.
    else if (PySlice_Check(obj)){
        Py_INCREF(obj);
        return obj;
    }
    // Translatable types have their context applied, but they can't be put in
    // the cache because they don't have a destructor that would remove them.
    else if (PyObject_IsInstance(obj,(PyObject *)&TranslatableType)){
        if (apply){
            return PyObject_CallMethod(obj,"_apply_context","O",context);
        } else {
            return PyObject_CallMethod(obj,"_remove_context","O",context);
        }
    }
    // Check if an outer wrap will cancel out an inner wrap
    else if (PyObject_IsInstance(obj,(PyObject *)&WrappedType) &&
             ((Wrapped *)obj)->wrapping_context == context &&
             ((Wrapped *)obj)->apply != apply){
        Py_INCREF(((Wrapped *)obj)->wrapped_obj);
        return ((Wrapped *)obj)->wrapped_obj;
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
        
        self = (PyObject *)PyDict_GetItem(wrapped_cache,
                                          (PyObject *)key);
        if (self){
            self = PyCObject_AsVoidPtr(self);
            Py_INCREF(self);
            Py_DECREF(key);
            return self;
        } else {
            self = Wrapped_new(&WrappedType,obj,context,apply);
            if (!self){
                Py_DECREF(key);
                return NULL;
            }

            PyObject *selfptr;
            selfptr = PyCObject_FromVoidPtr(self,NULL);
            if (!selfptr){
                Py_DECREF(key);
                return NULL;
            }

            if (PyDict_SetItem(wrapped_cache,(PyObject *)key,selfptr)){
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
_apply_remove_context(PyTypeObject *junk, PyObject *args){
    PyObject *obj,*context;
    int apply;

    if (!PyArg_ParseTuple(args, "OOi", &context, &obj, &apply))
        return NULL;

    return apply_remove_context(context,obj,apply);
}

PyObject *
wrap(PyTypeObject *junk, PyObject *args){
    PyObject *obj,*context;
    int apply = 1;

    if (!PyArg_ParseTuple(args, "OO|i", &obj, &context,&apply))
        return NULL; 

    return apply_remove_context(context,obj,apply);
}


#define xapply_context(self,obj) apply_remove_context(((Wrapped *)self)->wrapping_context,obj,((Wrapped *)self)->apply) 
#define xremove_context(self,obj) apply_remove_context(((Wrapped *)self)->wrapping_context,obj,!(((Wrapped *)self)->apply))

static PyObject *
Wrapped_getattr(Wrapped *self,PyObject *name){
    PyObject *r = NULL,*wr = NULL;

    r = PyObject_GetAttr(self->wrapped_obj,name);
    if (r == NULL){
        return NULL;
    }

    wr = xapply_context(self,r);
    Py_DECREF(r);
    return wr;
}

int
Wrapped_setattr(Wrapped *self,PyObject *name,PyObject *value){
    PyObject *unwrapped=NULL;
    int r;

    unwrapped = xremove_context(self,value);
    r = PyObject_SetAttr(self->wrapped_obj,name,unwrapped);
    Py_DECREF(unwrapped);

    return r;
}

static PyObject *
Wrapped_call(Wrapped *self,PyObject *args,PyObject *kwargs){
    int i;
    PyObject *unwrapped_args=NULL, *unwrapped_kwargs=NULL;
    PyObject *r,*wr;

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

    unwrapped_args = PyTuple_New(PyTuple_GET_SIZE(args));
    if (unwrapped_args == NULL) return NULL;
    for (i = 0; i < PyTuple_GET_SIZE(args); i++){
        PyObject *v = PyTuple_GET_ITEM(args,i),*w = NULL;

        w = xremove_context(self,v);
        PyTuple_SET_ITEM(unwrapped_args,i,w);
    }

    if (kwargs != NULL){
        unwrapped_kwargs = PyDict_New();
        if (!unwrapped_kwargs) return NULL;
        PyObject *k,*v;
        Py_ssize_t pos = 0;
        while (PyDict_Next(kwargs,&pos,&k,&v)){
            v = xremove_context(self,v);
            if (PyDict_SetItem(unwrapped_kwargs,k,v)) return NULL;
            Py_DECREF(v);
        }
    }

    r = PyObject_Call(self->wrapped_obj,unwrapped_args,unwrapped_kwargs);
    // Currently calling a un-callable Wrapped object gets to this point, but
    // with an exception, so the following DECREF's are important and may see
    // user code.
    Py_DECREF(unwrapped_args);
    Py_XDECREF(unwrapped_kwargs);
    if (r == NULL) return NULL;

    wr = xapply_context(self,r);
    Py_DECREF(r);

    return wr;
}

static PyObject *
Wrapped_str(Wrapped *self){
    return PyObject_Str(self->wrapped_obj);
}

static int
Wrapped_compare(Wrapped *self,PyObject *other){
    int r;
    PyObject *unwrapped;
    unwrapped = xremove_context(self,other);
    if (!unwrapped) return -2;
    r = PyObject_Compare(self->wrapped_obj,unwrapped);
    Py_DECREF(unwrapped);
    return r;
}

static PyObject *
Wrapped_repr(Wrapped *self){
    char buf[360];
    PyOS_snprintf(buf,sizeof(buf),
                  "<Wrapped at %p wrapping %.100s at %p with %.100s at %p>", self,
                  self->wrapped_obj->ob_type->tp_name,
                  self->wrapped_obj,
                  self->wrapping_context->ob_type->tp_name,
                  self->wrapping_context);
    return PyString_FromString(buf);
}

static long
Wrapped_hash(Wrapped *self){
    // Remember that a hash of an object *may* collide with another object. By
    // returning the hash of the wrapped object, that becomes much more likely,
    // but given that any given context will most likely only see either the
    // original object, or the wrapped verson, this is ok.
    return PyObject_Hash(self->wrapped_obj);
}


static Py_ssize_t
Wrapped_length(Wrapped *self){
    return PyObject_Length(self->wrapped_obj);
}

/* sequence slots */

static PyObject *
Wrapped_slice(Wrapped *self, Py_ssize_t i, Py_ssize_t j){
    return PySequence_GetSlice(self->wrapped_obj, i, j);
}

static int
Wrapped_ass_slice(Wrapped *self, Py_ssize_t i, Py_ssize_t j, PyObject *value){
    int r;
    PyObject *wr;
    wr = xremove_context(self,value);
    if (!wr) return -1;
    r = PySequence_SetSlice(self->wrapped_obj, i, j, wr);
    Py_DECREF(wr);
    return r;
}

static int
Wrapped_contains(Wrapped *self, PyObject *value){
    int r;
    PyObject *wvalue;
    wvalue = xremove_context(self,value);
    r = PySequence_Contains(self->wrapped_obj, wvalue);
    Py_DECREF(wvalue);
    return r;
}

static PySequenceMethods Wrapped_as_sequence = {
    (lenfunc)Wrapped_length,      /*sq_length*/
    0,                          /*sq_concat*/
    0,                          /*sq_repeat*/
    0,                          /*sq_item*/
    (ssizessizeargfunc)Wrapped_slice, /*sq_slice*/
    0,                          /*sq_ass_item*/
    (ssizessizeobjargproc)Wrapped_ass_slice, /*sq_ass_slice*/
    (objobjproc)Wrapped_contains, /* sq_contains */
};

PyObject *
Wrapped_getitem(Wrapped *self,PyObject *key){
    PyObject *unwrapped_key = NULL,*r = NULL,*wr = NULL;

    unwrapped_key = xremove_context(self,key);
    if (!unwrapped_key) goto bail;

    r = PyObject_GetItem(self->wrapped_obj,unwrapped_key);
    if (!r) goto bail;

    wr = xapply_context(self,r);

bail:
    Py_XDECREF(unwrapped_key);
    Py_XDECREF(r);
    return wr;
}

static int
Wrapped_ass_subscript(Wrapped *self, PyObject *key, PyObject *value){
    int r = -1;
    PyObject *wkey = NULL,*wvalue = NULL;
    wkey = xremove_context(self,key);
    if (!wkey) goto bail;
    if (value == NULL){
        if (!wvalue) goto bail;
        r = PyObject_DelItem(self->wrapped_obj, wkey);
    }
    else {
        wvalue = xremove_context(self,value);
        r = PyObject_SetItem(self->wrapped_obj, wkey, wvalue);
    }

bail:
    Py_XDECREF(wkey);
    Py_XDECREF(wvalue);
    return r;
}

static PyMappingMethods Wrapped_as_mapping = {
    (lenfunc)Wrapped_length,        /*mp_length*/
    (binaryfunc)Wrapped_getitem,                /*mp_subscript*/
    (objobjargproc)Wrapped_ass_subscript, /*mp_ass_subscript*/
};

/* iterator slots */

static PyObject *
Wrapped_iter(Wrapped *self){
    return xapply_context(self,PyObject_GetIter(self->wrapped_obj));
}

static PyObject *
Wrapped_iternext(Wrapped *self){
    return xapply_context(self,PyIter_Next(self->wrapped_obj));
}

PyTypeObject WrappedType = {
    PyObject_HEAD_INIT(NULL) // FIXME: s/NULL/&PyType_Type/ in weakrefobject.c, why?
    0,                         /*ob_size*/
    "wrapper.Wrapped",             /*tp_name*/
    sizeof(Wrapped),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)Wrapped_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    (cmpfunc)Wrapped_compare,           /*tp_compare*/
    (reprfunc)Wrapped_repr,              /*tp_repr*/
    0,                         /*tp_as_number*/
    &Wrapped_as_sequence,      /*tp_as_sequence*/
    &Wrapped_as_mapping,       /*tp_as_mapping*/
    (hashfunc)Wrapped_hash,              /*tp_hash */
    (ternaryfunc)Wrapped_call,              /*tp_call*/
    (reprfunc)Wrapped_str,               /*tp_str*/
    (getattrofunc)Wrapped_getattr,           /*tp_getattro*/
    (setattrofunc)Wrapped_setattr,           /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC, /*tp_flags*/ // FIXME: should Py_TPFLAGS_CHECKTYPES be defined here?
    "Wrap object in a context",           /* tp_doc */
    (traverseproc)Wrapped_traverse,     /* tp_traverse */
    (inquiry)Wrapped_clear,             /* tp_clear */
    0,		               /* tp_richcompare */
    offsetof(Wrapped, in_weakreflist),  /* tp_weaklistoffset */
    (getiterfunc)&Wrapped_iter,		               /* tp_iter */
    (iternextfunc)&Wrapped_iternext,		               /* tp_iternext */
    0,             /* tp_methods */
    0,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    0,      /* tp_init */
    0,                         /* tp_alloc */
    0,                         /* tp_new */
    PyObject_GC_Del, /* tp_free */
};

static PyMethodDef methods[] = {
    {"wrap", (PyCFunction)wrap, METH_VARARGS,
     "Wrap an object."},
    {"_apply_remove_context", (PyCFunction)_apply_remove_context, METH_VARARGS,
     NULL},
    {NULL,NULL,0,NULL}
};

PyObject *initwrapper(void){
    PyObject* m;

    wrapped_cache = PyDict_New();
    if (!wrapped_cache)
        return NULL;

    if (PyType_Ready(&WrappedType) < 0)
        return NULL;

    TranslatableType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&TranslatableType) < 0)
        return NULL;

    m = Py_InitModule3("Tuke.context.wrapper", methods,
                       "Object wrapping");
    if (!m) return NULL;

    Py_INCREF(&WrappedType);
    PyModule_AddObject(m, "Wrapped", (PyObject *)&WrappedType);
    PyModule_AddObject(m, "Translatable", (PyObject *)&TranslatableType);
    PyModule_AddObject(m, "_wrapped_cache",wrapped_cache);

    return m;
}

// Local Variables:
// mode: C
// fill-column: 76
// c-file-style: "gnu"
// indent-tabs-mode: nil
// End:
// vim: et:sw=4:sts=4:ts=4:cino=>4s,{s,\:s,+s,t0,g0,^-4,e-4,n-4,p4s,(0,=s:
