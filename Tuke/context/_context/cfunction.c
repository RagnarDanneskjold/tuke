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

PyObject *CFunction_new(PyObject *(*f)(void *closure,
                                       PyObject *args,
                                       PyObject *kwargs),
                        void (*fd)(void *closure),
                        void *closure){
    CFunction *self;
    self = (CFunction *)CFunctionType.tp_alloc(&CFunctionType, 0);

    self->in_weakreflist = NULL;

    self->f = f;
    self->fd = fd;
    self->closure = closure;
    return (PyObject *)self;
}

void CFunction_dealloc(CFunction *self){
    if (self->fd)
        self->fd(self->closure);
    if (self->in_weakreflist != NULL)
        PyObject_ClearWeakRefs((PyObject *) self);
    self->ob_type->tp_free((PyObject*)self);
}

PyObject *CFunction_call(CFunction *self,PyObject *args,PyObject *kwargs){
    return (self->f)(self->closure,args,kwargs);
}

PyTypeObject CFunctionType = {
    PyObject_HEAD_INIT(&PyType_Type)
    0,                         /*ob_size*/
    "Tuke.context._cfunction.CFunction",             /*tp_name*/
    sizeof(CFunction),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)CFunction_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,           /*tp_compare*/
    0,              /*tp_repr*/
    0,                         /*tp_as_number*/
    0,      /*tp_as_sequence*/
    0,       /*tp_as_mapping*/
    0,              /*tp_hash */
    (ternaryfunc)CFunction_call,              /*tp_call*/
    0,               /*tp_str*/
    0,           /*tp_getattro*/
    0,           /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT, /*tp_flags*/
    "Internal use only, see source code.", /* tp_doc */
    0,     /* tp_traverse */
    0,             /* tp_clear */
    0,		               /* tp_richcompare */
    offsetof(CFunction, in_weakreflist),  /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    0,             /* tp_methods */
    0,             /* tp_members */
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


// Test code
PyObject *test_func(void *closure,PyObject *args,PyObject *kwargs){
   Py_INCREF(*((PyObject **)closure));

   Py_RETURN_TRUE;
}
void test_func_dealloc(void *closure){
    Py_DECREF(*((PyObject **)closure));
    PyMem_Free(closure);
}

PyObject *test(PyObject *ignored){
    CFunction *f = NULL;
    PyObject *r = NULL;
    PyObject *obj = PyString_FromString(
"The cockatrice, which no one ever saw, was born by accident at the end of the \
twelfth century and died in the middle of the seventeenth, a victim of the new \
science.");
    PyObject **objp = NULL;
    if (!obj) goto bail;

    objp = PyMem_Malloc(sizeof(PyObject *));
    *objp = obj;
    Py_INCREF(obj);
    f = (CFunction *)CFunction_new(test_func,test_func_dealloc,objp);
    if (!f) goto bail;

    int i;
    for (i = 0; i < 10; i++){
        r = PyObject_CallObject((PyObject *)f,NULL);
        if (!r) goto bail;
        if (obj->ob_refcnt != 3){
            PyErr_SetString(PyExc_AssertionError,
                            "obj->ob_refcnt != 3");
            goto bail;
        }
        Py_DECREF(obj);
    }

    Py_DECREF(f); f = NULL;
    if (obj->ob_refcnt != 1){
        PyErr_SetString(PyExc_AssertionError,
                        "obj->ob_refcnt != 1 after dealloc");
        goto bail;
    }

    if (r != Py_True){
        PyErr_SetString(PyExc_AssertionError,
                        "r != Py_True");
        goto bail;
    }

    Py_XDECREF(obj);
    Py_XDECREF(f);
    Py_XDECREF(r);
    Py_RETURN_TRUE;
bail:
    Py_XDECREF(obj);
    Py_XDECREF(f);
    Py_XDECREF(r);
    return NULL;
}


static PyMethodDef methods[] = {
    {"test", (PyCFunction)test, METH_NOARGS,
     NULL},
    {NULL,NULL,0,NULL}
};

PyObject *initcfunction(void){
    PyObject* m;

    if (PyType_Ready(&CFunctionType) < 0)
        return NULL;

    m = Py_InitModule3("Tuke.context._context._cfunction", methods,
                       "Wrap a C function in a Python callable object.");
    if (!m) return NULL;

    PyModule_AddObject(m, "CFunction", (PyObject *)&CFunctionType);

    return m;
}

// Local Variables:
// mode: C
// fill-column: 76
// c-file-style: "gnu"
// indent-tabs-mode: nil
// End:
// vim: et:sw=4:sts=4:ts=4:cino=>4s,{s,\:s,+s,t0,g0,^-4,e-4,n-4,p4s,(0,=s:
