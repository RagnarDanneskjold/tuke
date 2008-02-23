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

"""Geometry transformations.

Geometry transformations are implemented by decorating every object method that
returns geometry with an appropriate type of transformation decoration.
Secondly to transform an object, use an appropriate transformation function.

Behind the scenes objects have a 'transform' attribute automatically added
and updated as needed. The decorators then apply transformations to the
geometry data before returning it.
"""

from Tuke import repr_helper
from Tuke import Element,Id

import shapely.geometry
import numpy

class Transformation:
    """Holder for geometry transformations.
    
    After applying a geometry transformation to a class instance a
    Transformation instance with the name 'transform' will be inserted into
    the objects dict.
    """

    def __init__(self,v = (0.0,0.0)):
        """Create geometry transformation.

        v - Translation vector.
        """
        self.v = v

    def __call__(self,v):
        """Apply the Transformation to v

        v may be a bare tuple, or tuple/list of tuples, or any other combo.
        """

        try:
            r = []
            for n in v:
               r.append(self(n))
            return type(v)(r)
        except TypeError:
            return (self.v[0] + v[0],self.v[1] + v[1])

    def __add__(self,other):
        """Apply the effects of other to self and return a transformation
        encompassing both."""

        r = Transformation()

        r.v = (self.v[0] + other.v[0],self.v[1] + other.v[1])

        return r

    def __eq__(self,other):
        return self.v == other.v

    def __ne__(self,other):
        return not self.__eq__(other)

    @repr_helper
    def __repr__(self):
        return (None,{'v':self.v})

def translate(e,v):
    """Translate element by vertex"""

    assert(isinstance(e,Element))
    assert(len(v) == 2)

    if not hasattr(e,'transform'):
        e.transform = Transformation(v = (0,0))

    e.transform.v = (e.transform.v[0] + v[0],
                       e.transform.v[1] + v[1])

    return e
