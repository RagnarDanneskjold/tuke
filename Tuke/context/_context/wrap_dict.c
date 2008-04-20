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

#include "wrapper.h"

PyObject *
wrap_dict(PyObject *context,PyObject *obj,int apply){
    // Dicts are not immutable, so this naive implementation breaks that.
    PyObject *r = PyDict_New();
    if (!r) return NULL;

    PyObject *k = NULL,*v = NULL;
    Py_ssize_t pos = 0;
    while (PyDict_Next(obj,&pos,&k,&v)){
        k = apply_remove_context(context,k,apply);
        if (!k) goto bail;
        v = apply_remove_context(context,v,apply);
        if (!v) goto bail;

        if (PyDict_SetItem(r,k,v)) goto bail;

        // = NULL for the bail routine
        Py_DECREF(v); v = NULL;
        Py_DECREF(k); k = NULL;
    }
    return r;

bail:
    Py_XDECREF(v);
    Py_XDECREF(k);
    Py_XDECREF(r);
    return NULL;
}

// Local Variables:
// mode: C
// fill-column: 76
// c-file-style: "gnu"
// indent-tabs-mode: nil
// End:
// vim: et:sw=4:sts=4:ts=4:cino=>4s,{s,\:s,+s,t0,g0,^-4,e-4,n-4,p4s,(0,=s:
