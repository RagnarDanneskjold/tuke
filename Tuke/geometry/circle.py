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

from Tuke import SingleElement,Id
import shapely.geometry

from math import sin,cos,pi

def arc_points(a,b,r,segments):
    """Approximates an arc from a to b with a given radius and a specified number of segments. Returns a tuple of vertexes."""
    assert(segments > 0)
    assert(a != b)
    assert(r)

    t = []

    i = a
    for j in range(segments + 1):
        t += [(cos(i) * r,sin(i) * r)]

        i += abs(b - a) / segments

    return t

class Circle(SingleElement):
    """A circle with a specified diameter."""

    full_class_name = 'Tuke.geometry.Circle'

    saved_state = SingleElement.saved_state + \
        ('dia','layer')

    def __init__(self,dia,layer=None,id=Id()):
        SingleElement.__init__(self,id=id)

        if not layer:
            raise Exception('Missing layer value')
        if not dia > 0:
            raise Exception('Diameter must be greater than zero')

        self.dia = float(dia)

        self.layer = layer
        
    def render(self):
        v = []

        v = arc_points(0,2*pi,self.dia / 2,32)

        p = shapely.geometry.Polygon(v)

        return [(self.id,self.layer,p)]
