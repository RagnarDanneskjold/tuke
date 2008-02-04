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

from Tuke.geometry.circle import arc_points 
from math import atan2,pi,degrees

def make_line_vertexes(a,b,thickness,segments):
    # first find the angle of the given line
    dx = b[0] - a[0]
    dy = b[1] - a[1]

    alpha = atan2(dy,dx)

    # create half-circles for either end
    arc_a = arc_points(alpha + pi/2,alpha - pi/2,float(thickness)/2,segments)  
    arc_b = arc_points(alpha - pi/2,alpha + pi/2,float(thickness)/2,segments)  

    # half circles aren't complete yet, need to shift them relative to the end
    # positions
    def t(v,a):
        return [(x + a[0],y + a[1]) for (x,y) in v]
    arc_a = t(arc_a,a)
    arc_b = t(arc_b,b)

    return arc_a + arc_b

class Line(SingleElement):
    """A line with a specified thickness."""

    full_class_name = 'Tuke.geometry.Line'

    saved_state = SingleElement.saved_state + \
            ('a','b','thickness','layer')

    def __init__(self,a,b,thickness,layer=None,id=Id()):
        SingleElement.__init__(self,id=id)

        if not layer:
            raise Exception('Missing layer value')
        if not thickness > 0:
            raise Exception('Thickness must be greater than zero')

        self.a = a
        self.b = b
        self.thickness = thickness
        self.layer = layer

    def render(self):
        p = make_line_vertexes(self.a,self.b,self.thickness,16)

        return [(self.id,self.layer,p)]

class ThinLine(Line):
    """A line who's thickness is a multiple of the minimum resolution on the output device."""

    full_class_name = 'Tuke.geometry.ThinLine'
