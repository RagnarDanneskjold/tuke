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

    """

    @classmethod
    def is_valid_endpoint(cls,other):
        return other in cls.valid_endpoint_types

    __required__ = ()
    __defaults__ = dict(a=None,b=None)

    def _init(self):
        """Initialize trace
        
        a,b - The endpoints.

        Upon return a and b will be setup correctly for the subclass.
        """

        if self.a is not None and self.b is not None:
            self.set_endpoints(self.a,self.b)
        elif self.a is None and self.b is None:
            pass
        else:
            raise ValueError("Must specify both end points if either specified")

    def set_endpoints(self,a,b):
        """Set endpoints after trace creation.

        The endpoints have to be set in the traces context, which can be
        difficult to figure out. For instance:

        a.b.c.add(BaseTrace(a=?,b=?,id=Id('t')))

        Easier is to add an unconnected trace, and then connect it's ends
        after:

        a.b.c.add(BaseTrace(id=Id('t')))
        a.b.c.t.set_endpoints(a.b.c.d,a.b.c.e)

        """

        self.a = ElementRef(self,a)
        self.b = ElementRef(self,b)
