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


static PyTypeObject WrappedType;

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
Wrapped_new(PyTypeObject *type, PyObject *obj, PyObject *context)
{
    Wrapped *self;

    self = (Wrapped *)type->tp_alloc(type, 0);

    Py_INCREF(obj);
    self->_wrapped_obj = obj;

    Py_INCREF(context);
    self->_wrapping_context = context;

    return (PyObject *)self;
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
        r =  Wrapped_new(&WrappedType,obj,context);
    }
    else if (PyTuple_Check(obj)){
        printf("tuple\n");
        r = obj;
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
        printf("tuple\n");
        r = obj;
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

WRAP_TERNARY(Wrapped_call, PyEval_CallObjectWithKeywords,apply_context,remove_context)

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
}

// Local Variables:
// mode: C
// fill-column: 76
// c-file-style: "gnu"
// indent-tabs-mode: nil
// End:
// vim: et:sw=4:sts=4:ts=4:cino=>4s,{s,\:s,+s,t0,g0,^-4,e-4,n-4,p4s,(0,=s:
