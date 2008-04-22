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

#include "cfunction.h"
#include "weakset.h"

PyObject *WeakSet_New(void){
    WeakSet *self;
    self = (WeakSet *)WeakSetType.tp_alloc(&WeakSetType, 0);
    self->set = self->selfref = NULL;

    self->set = PySet_New(NULL);
    if (!self->set) goto bail;

    self->selfref = PyWeakref_NewRef((PyObject *)self->set,NULL);
    if (!self->selfref) goto bail;

    return (PyObject *)self;
bail:
    Py_XDECREF(self->set);
    Py_XDECREF(self->selfref);
    Py_DECREF(self);
    return NULL;
}

void WeakSet_dealloc(WeakSet *self){
    if (self->in_weakreflist != NULL)
            PyObject_ClearWeakRefs((PyObject *) self);
    Py_XDECREF(self->set);
    Py_XDECREF(self->selfref);
    self->ob_type->tp_free((PyObject*)self);
}

int WeakSet_Contains(PyObject *self,PyObject *key){
    PyObject *ref = PyWeakref_NewRef((PyObject *)key,NULL);
    if (!ref) return -1;

    int r = PySet_Contains(((WeakSet *)self)->set,ref);
    Py_DECREF(ref);
    return r;
}

typedef struct {
    PyObject *setref;
} remover_closure;

PyObject *WeakSet_remover(void *closure,PyObject *args,PyObject *kwargs){
    remover_closure *self = (remover_closure *)closure;
    PyObject *key = NULL;

    // The set we were created to update may not exist anymore.
    PyObject *set = PyWeakref_GET_OBJECT(self->setref);
    if (set == Py_None) Py_RETURN_NONE;
    
    if (!PyArg_ParseTuple(args, "O",&key)) return NULL;

    // Remove ourselves from the set
    int r = PySet_Discard(set,key);
    if (r == -1) return NULL; // Propegate errors from PySet_Discard
    if (r == 0){
        PyErr_Format(PyExc_RuntimeError,
                     "WeakSet_remover: PySet_Discard didn't find key in set");
        return NULL;
    }

    Py_RETURN_NONE;
}

void WeakSet_remover_dealloc(void *closure){
    remover_closure *self = (remover_closure *)closure;
    Py_XDECREF(self->setref);
    PyMem_Free(self);
}

int WeakSet_Add(PyObject *_self,PyObject *key){
    WeakSet *self = (WeakSet *)_self;

    int r = WeakSet_Contains((PyObject *)self,key);
    if (r) return r; // This also propegates errors.

    remover_closure *closure = PyMem_Malloc(sizeof(remover_closure));
    closure->setref = self->selfref;
    Py_INCREF(closure->setref);
    PyObject *remover = CFunction_new(WeakSet_remover,
                                      WeakSet_remover_dealloc,
                                      closure);

    PyObject *ref = PyWeakref_NewRef((PyObject *)key,remover);
    if (!ref) goto bail;

    r = PySet_Add(self->set,ref);
    if (r) goto bail;

    r = 0;
    goto done;
bail:
    r = -1;
done:
    Py_XDECREF(remover);
    Py_XDECREF(ref);
    return r;
}


static PyMemberDef WeakSet_members[] = {
    {"set", T_OBJECT_EX, offsetof(WeakSet, set), 0,
    NULL},
    {"selfref", T_OBJECT_EX, offsetof(WeakSet, selfref), 0,
     NULL},
    {NULL}  /* Sentinel */
};

PyTypeObject WeakSetType = {
    PyObject_HEAD_INIT(&PyType_Type)
    0,                         /*ob_size*/
    "Tuke.context._weakset.WeakSet",             /*tp_name*/
    sizeof(WeakSet),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)WeakSet_dealloc, /*tp_dealloc*/
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
    Py_TPFLAGS_DEFAULT, /*tp_flags*/
    "Internal use only, see source code.", /* tp_doc */
    0,     /* tp_traverse */
    0,             /* tp_clear */
    0,		               /* tp_richcompare */
    offsetof(WeakSet, in_weakreflist),  /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    0,             /* tp_methods */
    WeakSet_members,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,    /* tp_dictoffset */
    0,      /* tp_init */
    0,                         /* tp_alloc */
    0,                         /* tp_new */
    0, /* tp_free */
};


PyObject *WeakSet_test(PyObject *ignored){
    int r;
    WeakSet *set = NULL;
    PyObject *obj = NULL;
    PyObject *setref = NULL;
    PyObject *setbackup = NULL;

    // It'd be nice if this had line numbers.
#define T(x) if (!(x)) {PyErr_SetString(PyExc_AssertionError,"FIXME"); goto bail;}

    obj = WeakSet_New(); 
    if (!obj) goto bail;

    set = (WeakSet *)WeakSet_New();
    if (!set) goto bail;
    setref = set->selfref;
    Py_INCREF(setref);
    T(setref->ob_refcnt == 2);
    T(PyObject_Length(set->set) == 0);
    T(WeakSet_Contains((PyObject *)set,obj) == 0);

    r = WeakSet_Add((PyObject *)set,obj);
    if (r) goto bail;
    T(setref->ob_refcnt == 3);
    T(PyObject_Length(set->set) == 1);
    T(WeakSet_Contains((PyObject *)set,obj) == 1);

    // Simple case, object is deleted while set is still alive.
    Py_CLEAR(obj);
    T(setref->ob_refcnt == 2);
    T(PyObject_Length(set->set) == 0);

    // Complex, set is deleted, while object is still alive.
    obj = WeakSet_New(); 
    if (!obj) goto bail;
    r = WeakSet_Add((PyObject *)set,obj);
    if (r) goto bail;
    T(PyObject_Length(set->set) == 1);
    T(WeakSet_Contains((PyObject *)set,obj) == 1);
    T(setref->ob_refcnt == 3);


    // If we simply delete set, the reference created for obj, and hence
    // setref, will have nothing pointing to it and be garbage collected before
    // set is actually deleted. So create a backup of the set, forcing the
    // reference created for obj to persist.
    setbackup = PySet_New(set->set);
    if (!setbackup) goto bail;

    Py_CLEAR(set);
    // The reference for obj is still holding a reference to setref
    T(setref->ob_refcnt == 2);

    Py_CLEAR(obj);
    // Now only we are holding a reference to setref
    T(setref->ob_refcnt == 1);


    Py_XDECREF(set);
    Py_XDECREF(setbackup);
    Py_XDECREF(setref);
    Py_XDECREF(obj);
    Py_RETURN_TRUE;
bail:
    Py_XDECREF(set);
    Py_XDECREF(setbackup);
    Py_XDECREF(setref);
    Py_XDECREF(obj);
    return NULL;
}


static PyMethodDef methods[] = {
    {"test", (PyCFunction)WeakSet_test, METH_NOARGS,
     NULL},
    {NULL,NULL,0,NULL}
};

PyObject *initweakset(void){
    PyObject* m;

    if (PyType_Ready(&WeakSetType) < 0)
        return NULL;

    m = Py_InitModule3("Tuke.context._context._weakset", methods,
                       "Weak key set.");
    if (!m) return NULL;

    PyModule_AddObject(m, "WeakSet", (PyObject *)&WeakSetType);

    return m;
}

// Local Variables:
// mode: C
// fill-column: 76
// c-file-style: "gnu"
// indent-tabs-mode: nil
// End:
// vim: et:sw=4:sts=4:ts=4:cino=>4s,{s,\:s,+s,t0,g0,^-4,e-4,n-4,p4s,(0,=s:
