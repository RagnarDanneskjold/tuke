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

// context.Source objects are sub-classed by Element and are used to hold
// context. They provide two main functions to that end. First they allow for
// attributes to be shadowed. This is implemented with a __dict_shadow__ who's
// values override __dict__ for getattrss, but not setattrs. This allows
// attributes to be set to identities in the Elements context, while to the
// outside world they have a value. For instance for the code in an Element, id
// is always Id('.') while to the outside context it may be set to various
// things.
//
// The second function is to provide a notify-on-change callback system for any
// attribute in the Source __dict__ This is used in a variety of contexts when
// changes need to be monitored.
//
//
// A "cute party trick" is the special __shadowless__ attribute. It's a second
// Source object, created alongside the regular Source object, with an empty
// __dict_shadow__ This is used in the wrapper code to quickly give
// _(apply|remove)_context functions access to the un-shadowed attributes of a
// Source object.

PyObject *readonly_empty_dict = NULL;

PyObject *
Source_new(PyTypeObject *type, PyObject *args, PyObject *kwargs){
    Source *self;
    if (!PyArg_ParseTuple(args, ""))
        return NULL;

    // self->shadowless is created alongside self.
    //
    // This isn't as weird as it looks. It's not much different than normally
    // creating objects within an object, we treat refcounts exactly as we
    // would with any other sub-object, the difference being the creation is
    // interleaved and self-referential.
    
    self = (Source *)type->tp_alloc(type, 0);

    // shadowless is created with a refcnt of 1
    self->shadowless = (Source *)type->tp_alloc(type, 0);

    // Seperate weakreflists, as that stuff is handled by the weakref code.
    self->in_weakreflist = NULL;
    self->shadowless->in_weakreflist = NULL;

    // Creating the master set of dicts.
    self->dict = PyDict_New();
    if (!self->dict) return NULL;
    self->dict_shadow = PyDict_New();
    if (!self->dict_shadow) return NULL;
    self->dict_callbacks = PyDict_New();
    if (!self->dict_callbacks) return NULL;

    // shadowless shares __dict__ and __dict_callbacks__, so increment the
    // reference counts and set pointers.
    Py_INCREF(self->dict);
    self->shadowless->dict = self->dict;
    Py_INCREF(self->dict_callbacks);
    self->shadowless->dict_callbacks = self->dict_callbacks;

    // shadowless still has to have it's own valid shadow dict, so we use a
    // pre-made, empty, read-only dict.
    Py_INCREF(readonly_empty_dict);
    self->shadowless->dict_shadow = readonly_empty_dict;

    // shadowless also has to point to something, so point it itself, which
    // means another reference.
    Py_INCREF(self->shadowless);
    self->shadowless->shadowless = self->shadowless;

    return (PyObject *)self;
}

// In the following dealloc stuff notice how shadowless is treated completely
// normally? Since we setup all the reference counts correctly, we can use the
// standard garbage collection code. On dealloc the master, shadowed instance,
// gets dealloced immediately, then the garbage collector later removes the
// shadowless instance, with its internal self-reference after the usual
// traverse and clear.
static void
Source_dealloc(Source* self){
    PyObject_GC_UnTrack(self);
    if (self->in_weakreflist != NULL)
            PyObject_ClearWeakRefs((PyObject *) self);
    Py_XDECREF(self->dict);
    Py_XDECREF(self->dict_shadow);
    Py_XDECREF(self->dict_callbacks);
    Py_XDECREF(self->shadowless);
    PyObject_GC_Del(self);
}

static int
Source_traverse(Source *self, visitproc visit, void *arg){
    Py_VISIT(self->dict);
    Py_VISIT(self->dict_shadow);
    Py_VISIT(self->dict_callbacks);
    Py_VISIT(self->shadowless);
    return 0;
}

static int
Source_clear(Source *self){
    Py_CLEAR(self->dict);
    Py_CLEAR(self->dict_shadow);
    Py_CLEAR(self->dict_callbacks);
    Py_CLEAR(self->shadowless);
    return 0;
}

static PyMemberDef Source_members[] = {
    {"__dict__", T_OBJECT_EX, offsetof(Source, dict), 0,
     NULL},
    {"__dict_shadow__", T_OBJECT_EX, offsetof(Source, dict_shadow), 0,
     NULL},
    {"__dict_callbacks__", T_OBJECT_EX, offsetof(Source, dict_callbacks), 0,
     NULL},
    {"__shadowless__", T_OBJECT_EX, offsetof(Source, shadowless), 0,
     NULL},
    {NULL}  /* Sentinel */
};

static PyObject *
source_notify_callback_entry_destroyer(void *closure,
                                       PyObject *args,PyObject *kwargs){
    PyObject *callbacks = (PyObject *)closure;
    PyObject *key;

    if (!PyArg_ParseTuple(args, "O",&key)) return NULL;

    if (PySet_Discard(callbacks,key)){
        PyErr_Clear();
    }

    Py_RETURN_NONE;
}
static void
source_notify_callback_entry_destroyer_destroyer(void *closure){
    Py_DECREF((PyObject *)closure);
}

static PyObject *
source_notify(Source *self,PyObject *args,PyObject *kwargs){
    if (self->dict_shadow == readonly_empty_dict){
        PyErr_SetString(PyExc_TypeError,
                        "Source.__shadowless__.notify() is not supported.");
        return NULL;
    }

    PyObject *r;
    // Arguments, borrowed references:
    PyObject *attr,
             *callback;

    // References owned by us. decrefed at the end:    
    PyObject *attr_callbacks = NULL,
             *callback_ref = NULL,
             *cb_destroyer = NULL;

    if (!PyArg_ParseTuple(args, "OO", 
                          &attr, 
                          &callback))
        return NULL;

    if (!PyString_CheckExact(attr)){
        PyErr_Format(PyExc_TypeError,
                     "attribute must be string, not %s",
                     attr->ob_type->tp_name);
        goto bail;
    }
    if (!PyCallable_Check(callback)){
        PyErr_Format(PyExc_TypeError,
                     "callback must be callable, not %s",
                     callback->ob_type->tp_name);
        goto bail;
    }

    attr_callbacks = PyDict_GetItem(self->dict_callbacks,attr);
    if (!attr_callbacks){
        attr_callbacks = PySet_New(NULL);
        if (PyDict_SetItem(self->dict_callbacks,attr,attr_callbacks))
                goto bail;
    }

    Py_INCREF(attr_callbacks);
    cb_destroyer = CFunction_new(source_notify_callback_entry_destroyer,
                                 source_notify_callback_entry_destroyer_destroyer,
                                 attr_callbacks);
    callback_ref = PyWeakref_NewRef(callback,cb_destroyer);
    if (!callback_ref) goto bail;

    if (PySet_Add(attr_callbacks,callback_ref)) goto bail;

    Py_INCREF(Py_None);
    r = Py_None;
    goto cleanup;
bail:
    r = NULL;
cleanup:
    Py_XDECREF(attr_callbacks);
    Py_XDECREF(callback_ref);
    Py_XDECREF(cb_destroyer);
    return r;
}

static PyMethodDef Source_methods[] = {
    {"_source_notify", (PyCFunction)source_notify, METH_VARARGS,
     ""}, // FIXME
    {NULL,NULL,0,NULL}
};

static PyObject *
source_getattro(Source *self,PyObject *name){
    PyObject *r;

    if (self->dict_shadow != readonly_empty_dict){
        r = PyDict_GetItem(self->dict_shadow,name);
        if (r) {
            Py_INCREF(r);
            return r;
        }
    }

    return PyObject_GenericGetAttr((PyObject *)self,name);
}

static int
source_setattro(Source *self,PyObject *name,PyObject *value){
    int r; 
    PyObject *attr_callbacks = NULL,
             *cbref = NULL,
             *cb = NULL,
             *cr;

    if (self->dict_shadow == readonly_empty_dict){
        PyErr_SetString(PyExc_TypeError,
                        "Source.__shadowless__ is read only.");
        return -1;
    }

    r = PyObject_GenericSetAttr((PyObject *)self,name,value);
    if (r) goto bail;

    // Note that the callbacks are called *after* the value has been set,
    // allowing the callbacks to see the new value.

    attr_callbacks = PyDict_GetItem(self->dict_callbacks,name);
    if (attr_callbacks){
        // Calling the callbacks may generate new ones, so clear the list first.
        Py_INCREF(attr_callbacks);
        if (PyDict_DelItem(self->dict_callbacks,name)) goto bail;

        while (PySet_GET_SIZE(attr_callbacks)){
            cbref = PySet_Pop(attr_callbacks);
            if (!cbref) goto bail;

            cb = PyWeakref_GetObject(cbref);
            Py_INCREF(cb);
            Py_DECREF(cbref);
            cbref = NULL;
            if (cb == Py_None){
                PyErr_SetString(PyExc_RuntimeError,
                                "Callback reference points to dead object.");
                goto bail; 
            }

            cr = PyObject_CallObject(cb,NULL);
            if (!cr) goto bail;
            Py_DECREF(cr);
            Py_DECREF(cb);
            cb = NULL;
        }
    }

    goto cleanup;
bail:
    r = -1;
cleanup:
    Py_XDECREF(attr_callbacks);
    Py_XDECREF(cbref);
    Py_XDECREF(cb);
    return r;
}

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
    source_getattro,           /*tp_getattro*/
    source_setattro,           /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "Internal use only, see source code.", /* tp_doc */
    (traverseproc)Source_traverse,     /* tp_traverse */
    (inquiry)Source_clear,             /* tp_clear */
    0,		               /* tp_richcompare */
    offsetof(Source, in_weakreflist),  /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    Source_methods,             /* tp_methods */
    Source_members,             /* tp_members */
    0,                         /* tp_getset */
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


static PyMethodDef methods[] = {
    {NULL,NULL,0,NULL}
};

PyObject *initsource(void){
    PyObject* m;

    if (PyType_Ready(&SourceType) < 0)
        return NULL;

    PyObject *tmp = PyDict_New();
    if (!tmp) return NULL;
    readonly_empty_dict = PyDictProxy_New(tmp);
    Py_DECREF(tmp);
    if (!readonly_empty_dict) return NULL;

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
