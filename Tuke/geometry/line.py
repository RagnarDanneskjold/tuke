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

from Tuke.geometry import Geometry

from Tuke.geometry.circle import arc_points 
from math import atan2,pi,degrees

def make_line_vertexes(a,b,thickness,segments):
    # first find the angle of the given line
    d = b - a

    alpha = atan2(d[0,1],d[0,0])

    # create half-circles for either end
    arc_a = arc_points(alpha + pi/2,alpha - pi/2,float(thickness)/2,segments)  
    arc_b = arc_points(alpha - pi/2,alpha + pi/2,float(thickness)/2,segments)  

    # half circles aren't complete yet, need to shift them relative to the end
    # positions
    def t(vs,a):
        return [v + a for v in vs]
    arc_a = t(arc_a,a)
    arc_b = t(arc_b,b)

    return arc_a + arc_b

class Line(Geometry):
    """A line with a specified thickness."""

    def __init__(self,a,b,thickness,layer='',id=''):
        Geometry.__init__(self,layer=layer,id=id)

        if not thickness > 0:
            raise ValueError, 'Thickness must be greater than zero: %d' % thickness

        self.a = a
        self.b = b
        self.thickness = thickness

    def render(self):
        v = make_line_vertexes(self.a,self.b,self.thickness,16)

        return (v,())

class ThinLine(Line):
    """A line who's thickness is a multiple of the minimum resolution on the output device."""
    pass
