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

// Source provides a way to store the three variables that provide context to
// each Element, id, transform, and parent. There are a number of subtle
// properties at play here, your first step in understanding the interplay of
// Element and Source is to read the Element.__new__ code.

#include <Python.h>
#include "structmember.h"

#include "source.h"
#include "cfunction.h"
#include "wrapper.h"

PyObject *source_callbacks = NULL;
PyObject *transform_str,*parent_str;

static int
notify_member_callbacks(PyObject *self,PyObject *attr){
    int r,pos;
    PyObject *selfref = NULL,
             *callbacks_by_obj = NULL,
             *callbacks_for_attr = NULL,
             *cb_copy = NULL,
             *key = NULL,*value = NULL;

    selfref = PyWeakref_NewRef(self,NULL);
    if (!selfref) goto bail; // shouldn't happen

    // Either of the next two gets may fail, that just means that no callbacks
    // were found.
    callbacks_by_obj = PyDict_GetItem(source_callbacks,selfref);
    if (!callbacks_by_obj) goto done;

    callbacks_for_attr = PyDict_GetItem(callbacks_by_obj,attr);
    if (!callbacks_for_attr) goto done;


    // The callbacks may create more callbacks, so first clear the callbacks
    // list. 
    cb_copy = callbacks_for_attr;
    Py_INCREF(cb_copy);
    callbacks_for_attr = PyDict_New();
    if (!callbacks_for_attr) goto bail;
    if (PyDict_SetItem(callbacks_by_obj,attr,callbacks_for_attr)) goto bail;
    
    pos = 0;
    while (PyDict_Next(cb_copy,&pos,&key,&value)){
        if (PyWeakref_GET_OBJECT(key) != Py_None){
            value = PyObject_CallFunction(value,"(O)",PyWeakref_GET_OBJECT(key));
            if (!value) {
                goto bail;
            } else {
                Py_DECREF(value);
            }
        }
    }

done:
    r = 0;
    goto cleanup;
bail:
    r = -1;
cleanup:
    Py_XDECREF(selfref);
    Py_XDECREF(callbacks_for_attr);
    return r;
}


static void
Source_dealloc(Source* self){
    PyObject_GC_UnTrack(self);
    if (self->in_weakreflist != NULL)
            PyObject_ClearWeakRefs((PyObject *) self);
    Py_XDECREF(self->dict);
    Py_XDECREF(self->id);
    Py_XDECREF(self->id_real);
    Py_XDECREF(self->transform);
    Py_XDECREF(self->transform_real);
    Py_XDECREF(self->parent);
    PyObject_GC_Del(self);
}

static int
Source_traverse(Source *self, visitproc visit, void *arg){
    Py_VISIT(self->dict);
    Py_VISIT(self->id);
    Py_VISIT(self->id_real);
    Py_VISIT(self->transform);
    Py_VISIT(self->transform_real);
    Py_VISIT(self->parent);
    return 0;
}

static int
Source_clear(Source *self){
    PyObject *selfref = PyWeakref_NewRef((PyObject *)self,NULL); 
    if (!selfref) return -1;
    if (PyDict_DelItem(source_callbacks,selfref)){
        // It's possible for Source_clear to be called more than once.
        PyErr_Clear();
    }
    Py_DECREF(selfref);

    Py_CLEAR(self->dict);
    Py_CLEAR(self->id);
    Py_CLEAR(self->id_real);
    Py_CLEAR(self->transform);
    Py_CLEAR(self->transform_real);
    Py_CLEAR(self->parent);
    return 0;
}

PyObject *
Source_new(PyTypeObject *type, PyObject *args, PyObject *kwargs){
    Source *self;
    PyObject *id,*transform,*parent;

    self = PyObject_GC_New(Source,type);
    self->in_weakreflist = NULL;

    self->dict = PyDict_New();
    if (!self->dict) return NULL;

    if (!PyArg_ParseTuple(args, "OOO", &id, &transform, &parent))
        return NULL;

    Py_INCREF(id); self->id = id;
    Py_INCREF(id); self->id_real = id;
    Py_INCREF(transform); self->transform = transform;
    Py_INCREF(transform); self->transform_real = transform;
    Py_INCREF(parent); self->parent = parent;

    PyObject_GC_Track(self);
    return (PyObject *)self;
}

#define GETTER(name) \
    static PyObject * \
    Source_get_##name(Source *self,void *closure){\
        Py_INCREF(self->name); \
        return self->name; \
    }

#define SETTER(name,namestr) \
    static int \
    Source_set_##name(Source *self, PyObject *value, void *closure){\
        if (namestr && notify_member_callbacks((PyObject *)self,namestr)) \
            return -1; \
        Py_DECREF(self->name##_real); \
        Py_INCREF(value); \
        self->name##_real = value; \
        return 0; \
    }

#define DEF_GET_SET(name,namestr) \
    SETTER(name,namestr) \
    GETTER(name) \
    GETTER(name##_real)


DEF_GET_SET(id,NULL)
DEF_GET_SET(transform,transform_str)


// Parent is not masked
static PyObject *
Source_get_parent(Source *self, void *closure){
    Py_INCREF(self->parent);
    return self->parent;
}

static int
Source_set_parent(Source *self, PyObject *value, void *closure){
    if (notify_member_callbacks((PyObject *)self,parent_str)) return -1;
    Py_DECREF(self->parent);
    Py_INCREF(value);
    self->parent = value;
    return 0;
}

static PyGetSetDef Source_getseters[] = {
    {"id",
     (getter)Source_get_id, (setter)Source_set_id,
     "Identifier",
     NULL},
    {"_id_real",
     (getter)Source_get_id_real, NULL,
     "Identifier",
     NULL},
    {"transform",
     (getter)Source_get_transform, (setter)Source_set_transform,
     "Geometry transformation",
     NULL},
    {"_transform_real",
     (getter)Source_get_transform_real, NULL,
     "Geometry transformation",
     NULL},
    {"parent",
     (getter)Source_get_parent, (setter)Source_set_parent,
     "Parent",
     NULL},
    {NULL}
};

static PyMemberDef Source_members[] = {
    {"__dict__", T_OBJECT_EX, offsetof(Source, dict), 0,
     NULL},
    {NULL}  /* Sentinel */
};

PyTypeObject SourceType = {
    PyObject_HEAD_INIT(&PyType_Type)
    0,                         /*ob_size*/
    "Tuke.context.source.Source",             /*tp_name*/
    sizeof(Source),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)Source_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,           /*tp_compare*/
    0,              /*tp_repr*/
    0,                         /*tp_as_number*/
    0,      /*tp_as_sequence*/
    0,       /*tp_as_mapping*/
    0,              /*tp_hash */
    0,              /*tp_call*/
    0,               /*tp_str*/
    0,           /*tp_getattro*/
    0,           /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "Internal use only, see source code.", /* tp_doc */
    (traverseproc)Source_traverse,     /* tp_traverse */
    (inquiry)Source_clear,             /* tp_clear */
    0,		               /* tp_richcompare */
    offsetof(Source, in_weakreflist),  /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    0,             /* tp_methods */
    Source_members,             /* tp_members */
    Source_getseters,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    offsetof(Source, dict),    /* tp_dictoffset */
    0,      /* tp_init */
    0,                         /* tp_alloc */
    Source_new,                         /* tp_new */
    PyObject_GC_Del, /* tp_del */
};

static PyObject *
callback_entry_destroyer(void *closure,PyObject *args,PyObject *kwargs){
    PyObject *callbacks = (PyObject *)closure;
    PyObject *key;

    if (!PyArg_ParseTuple(args, "O",&key)) return NULL;

    if (PyDict_DelItem(callbacks,key)){
        PyErr_Clear();
    }

    Py_RETURN_NONE;
}
static void
callback_entry_destroyer_destroyer(void *closure){
    Py_DECREF((PyObject *)closure);
}

PyObject *
unwrap(PyObject *o){ 
    while (o->ob_type == &WrappedType)
        o = ((Wrapped *)o)->wrapped_obj;
    return o;
}

static PyObject *
notify(PyObject *junk,PyObject *args,PyObject *kwargs){
    PyObject *r;

    // Arguments, borrowed references
    PyObject *self,
             *attr,
             *callback_callable,
             *callback_self;

    // References created by us, DECREFed at the end.
    PyObject *selfref = NULL,
             *callback_selfref = NULL,
             *callbacks_by_attr = NULL,
             *callbacks_for_attr = NULL,
             *cb_destroyer = NULL;

    if (!PyArg_ParseTuple(args, "OOOO", 
                          &self, &attr, 
                          &callback_self, &callback_callable))
        return NULL;

    if (!PyString_CheckExact(attr)){
        PyErr_Format(PyExc_TypeError,
                     "attribute must be string, not %s",
                     attr->ob_type->tp_name);
        goto bail;
    }
    if (!PyCallable_Check(callback_callable)){
        PyErr_Format(PyExc_TypeError,
                     "callback must be callable, not %s",
                     callback_callable->ob_type->tp_name);
        goto bail;
    }
    if (!(attr == transform_str ||
           attr == parent_str)){
        PyErr_Format(PyExc_ValueError,
                     "%s is not a valid attribute to notify on.",
                     PyString_AsString(attr));
        goto bail;
    }


    // self may be wrapped, unwrap fully 
    self = unwrap(self);

    selfref = PyWeakref_NewRef(self,NULL);
    if (!selfref) goto bail; // shouldn't happen

    // The following are both created on demand:
    callbacks_by_attr = PyDict_GetItem(source_callbacks,selfref);
    if (!callbacks_by_attr){
        callbacks_by_attr = PyDict_New();
        if (PyDict_SetItem(source_callbacks,selfref,callbacks_by_attr))
            goto bail;
    }
    callbacks_for_attr = PyDict_GetItem(callbacks_by_attr,attr);
    if (!callbacks_for_attr){
        callbacks_for_attr = PyDict_New();
        if (PyDict_SetItem(callbacks_by_attr,attr,callbacks_for_attr))
            goto bail;
    }

    // callback_self has a reference made too it. The callback, passed to
    // NewRef, then has the job of removing the callback entry if callback_self
    // is destroyed.
    Py_INCREF(callbacks_for_attr);
    cb_destroyer = CFunction_new(callback_entry_destroyer,
                                 callback_entry_destroyer_destroyer,
                                 callbacks_for_attr);
    callback_selfref = PyWeakref_NewRef(callback_self,cb_destroyer);
    if (!callback_selfref) goto bail;

    // And put it into the callback list
    if (PyDict_SetItem(callbacks_for_attr,callback_selfref,callback_callable))
        goto bail;

    Py_INCREF(Py_None);
    r = Py_None;
    goto cleanup;
bail:
    r = NULL;
cleanup:
    Py_XDECREF(selfref);
    Py_XDECREF(callback_selfref);
    Py_XDECREF(cb_destroyer);
    return r;
}

static PyMethodDef methods[] = {
    {"notify", (PyCFunction)notify, METH_VARARGS,
     ""}, // FIXME
    {NULL,NULL,0,NULL}
};

PyObject *initsource(void){
    PyObject* m;

    if (PyType_Ready(&SourceType) < 0)
        return NULL;

    source_callbacks = PyDict_New();
    if (!source_callbacks) return NULL;

    transform_str = PyString_InternFromString("transform");
    parent_str = PyString_InternFromString("parent");

    m = Py_InitModule3("Tuke.context._context.source", methods,
                       "Context source");
    if (!m) return NULL;

    PyModule_AddObject(m, "Source", (PyObject *)&SourceType);

    return m;
}

// Local Variables:
// mode: C
// fill-column: 76
// c-file-style: "gnu"
// indent-tabs-mode: nil
// End:
// vim: et:sw=4:sts=4:ts=4:cino=>4s,{s,\:s,+s,t0,g0,^-4,e-4,n-4,p4s,(0,=s:
