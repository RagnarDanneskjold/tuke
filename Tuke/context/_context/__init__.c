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

#include "cfunction.h"
#include "source.h"
#include "weakset.h"
#include "wrapper.h"

static PyMethodDef methods[] = {
    //{"wrap", (PyCFunction)wrap, METH_VARARGS,
    // "Wrap an object."},
    {NULL,NULL,0,NULL}
};

#ifndef PyMODINIT_FUNC	// declarations for DLL import/export
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
init_context(void){
    PyObject *m,
             *cfunction_module = NULL,
             *source_module = NULL,
             *weakset_module = NULL,
             *wrapper_module = NULL;

    m = Py_InitModule3("Tuke.context._context", methods,
                       "Object context, internal C extension.");
    if (m == NULL) goto bail;


    cfunction_module = initcfunction();
    if (!cfunction_module) goto bail;
    PyModule_AddObject(m, "_cfunction",
                       cfunction_module);

    source_module = initsource();
    if (!source_module) goto bail;
    PyModule_AddObject(m, "_source",
                       source_module);

    weakset_module = initweakset();
    if (!weakset_module) goto bail;
    PyModule_AddObject(m, "_weakset",
                       weakset_module);

    wrapper_module = initwrapper();
    if (!wrapper_module) goto bail;
    PyModule_AddObject(m, "wrapper",
                       wrapper_module);

bail:
    return;
//    Py_XDECREF(wrapper_module);
}

// Local Variables:
// mode: C
// fill-column: 76
// c-file-style: "gnu"
// indent-tabs-mode: nil
// End:
// vim: et:sw=4:sts=4:ts=4:cino=>4s,{s,\:s,+s,t0,g0,^-4,e-4,n-4,p4s,(0,=s:
