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

Behind the scenes objects have a 'transformed' attribute automatically added
and updated as needed. The decorators then apply transformations to the
geometry data before returning it.
"""

from Tuke import repr_helper
from Tuke import Element,Id

import shapely.geometry

class Transformation:
    """Holder for geometry transformations.
    
    After applying a geometry transformation to a class instance a
    Transformation instance with the name 'transformed' will be inserted into
    the objects dict.
    """

    def __init__(self,v = None):
        """Create geometry transformation.

        v - Translation vector.
        """
        self.v = v

    @repr_helper
    def __repr__(self):
        return (None,{'v':self.v})

def transform_render(fn):
    """Element.render() geometry transformation decorator"""
    def f(self):
        geo = fn(self)

        if not hasattr(self,'transformed'):
            return geo

        v = geo.transformed.v

        gnew = []
        for i,l,s in geo:
            # some shape-specific knowledge
            coords = []
            if isinstance(s,shapely.geometry.Polygon):
                for x,y in s.exterior.coords:
                    coords += [(x + v[0],y + v[1])]

                # make a new polygon
                s = shapely.geometry.Polygon(coords)

            gnew += [(i,l,s)]

        return gnew

    return f

def translate(e,v):
    """Translate element by vertex"""

    assert(isinstance(e,Element))
    assert(len(v) == 2)

    if not hasattr(e,'transformed'):
        e.transformed = Transformation(v = (0,0))

    e.transformed.v = (e.transformed.v[0] + v[0],
                       e.transformed.v[1] + v[1])

    return e
