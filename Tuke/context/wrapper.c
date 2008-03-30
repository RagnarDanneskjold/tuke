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
    PyObject *_wrapped_obj;
    PyObject *_wrapping_context;
} Wrapped;

static void
Wrapped_dealloc(Wrapped* self)
{
    Py_XDECREF(self->_wrapped_obj);
    Py_XDECREF(self->_wrapping_context);
}

static PyObject *
Wrapped_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    Wrapped *self;
    PyObject *obj=NULL, *context=NULL;

    if (! PyArg_ParseTuple(args, "OO", &obj, &context))
        return NULL; 

    self = (Wrapped *)type->tp_alloc(type, 0);

    if (obj == NULL || context == NULL){
        return NULL;
    }

    Py_INCREF(obj);
    self->_wrapped_obj = obj;

    Py_INCREF(context);
    self->_wrapping_context = context;

    return (PyObject *)self;
}

static PyObject *
Wrapped_getattr(Wrapped *self,PyObject *name){
    return PyObject_GetAttr(self->_wrapped_obj,name);
}

static PyObject *
Wrapped_setattr(Wrapped *self,PyObject *name,PyObject *value){
    return PyObject_SetAttr(self->_wrapped_obj,name,value);
}

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
    0,                         /*tp_compare*/
    Wrapped_repr,              /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    Wrapped_getattr,           /*tp_getattro*/
    Wrapped_setattr,           /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT, /*tp_flags*/
    "Wrap object in a context",           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
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
    Wrapped_new,                 /* tp_new */
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

    if (PyType_Ready(&WrappedType) < 0)
        return;

    m = Py_InitModule3("wrapper", methods,
                       "Object wrapping");

    if (m == NULL)
        return;

    Py_INCREF(&WrappedType);
    PyModule_AddObject(m, "Wrapped", (PyObject *)&WrappedType);
}

// Local Variables:
// mode: C
// fill-column: 76
// c-file-style: "gnu"
// indent-tabs-mode: nil
// End:
// vim: et:sw=4:sts=4:ts=4:cino=>4s,{s,\:s,+s,t0,g0,^-4,e-4,n-4,p4s,(0,=s:
