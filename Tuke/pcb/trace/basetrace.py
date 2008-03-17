# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
# ### BOILERPLATE ###
# Tuke - Electrical Design Automation toolset
# Copyright (C) 2008 Peter Todd <pete@petertodd.org>
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ### BOILERPLATE ###

from Tuke import Element,ElementRef

class BaseTrace(Element):
    """Base class for traces
    
    A trace is a way of electrically connecting two points on a circuit board.
    All traces have two end points, a and b, which are stored as ElementRefs.
    Trace objects are kept quite low level to keep them simple, functions are
    provided to manipulate and create groups of connected traces in a higher
    level way.

    valid_endpoint_types - Endpoints will be checked against this.
    """

    class InvalidEndpointTypeError(Exception):
        """Trace endpoint type cannot be connected to."""
        def __init__(self,endpoint_class,bad_endpoints):
            """Create exception.

            cls - Class of endpoint type requested.
            bad_endpoints - Set of the invalid endpoint objects.
            """
            Exception.__init__(self)

            assert isinstance(endpoint_class,type)
            self.endpoint_class = endpoint_class
            assert len(bad_endpoints)
            self.bad_endpoints = bad_endpoints

        def __str__(self):
            def t(elem):
                # FIXME: breaks layering in a nasty way... stupid
                # ElementWrappers
                try:
                    return type(elem._obj)
                except AttributeError:
                    return type(elem)

            ends = ','.join([str(t(e)) for e in self.bad_endpoints])
            return '%s: invalid endpoint(s) for traces of type %s' % (ends,self.endpoint_class)

    valid_endpoint_types = ()
    @classmethod
    def is_valid_endpoint(cls,other):
        return other in cls.valid_endpoint_types

    def __init__(self,a,b,id=None):
        """Initialize trace
        
        a,b - The endpoints.

        Upon return a and b will be setup correctly for the subclass.
        """
        Element.__init__(self,id=id)

        bad_endpoints = []
        for e in (a,b):
            if not isinstance(e,self.valid_endpoint_types):
                bad_endpoints.append(e)
        if bad_endpoints:
            raise BaseTrace.InvalidEndpointTypeError(self.__class__,set(bad_endpoints))

        self.a = ElementRef(a.id,a)
        self.b = ElementRef(b.id,b)

