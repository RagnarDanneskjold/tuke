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

from Tuke import Element,Id
from Tuke.geometry import Polygon,V

class Pad(Element):
    """Defines a pad"""

    def __init__(self,a,b,thickness,clearance,mask,id=Id()):
        """Create a pad.

        a - First point of line segment
        b - Second point
        thickness - Width of metal surrounding line segment
        clearance - Separation of pad from other conductors
        mask - Width of solder mask relief

        id - Id name
        """

        Element.__init__(self,id=id)

        self.a = a
        self.b = b
        self.thickness = thickness
        self.clearance = clearance
        self.mask = mask

        self.add(self.from_ab(self.thickness,layer='top.pad'))
        self.add(self.from_ab(self.thickness + (self.clearance * 2),layer='top.clearance'))
        self.add(self.from_ab(self.mask,layer='top.mask'))

    def from_ab(self,thickness,id=Id(),layer=None):
        """Returns a box generated from a,b with a given thickness.

        For makng pads, clearances etc.
        """

        return Polygon((V(self.a[0] - thickness/2,self.a[1] - thickness/2),
            V(self.b[0] + thickness/2,self.b[1] - thickness/2),
            V(self.b[0] + thickness/2,self.b[1] + thickness/2),
            V(self.a[0] - thickness/2,self.a[1] + thickness/2)),id=id,layer=layer)
