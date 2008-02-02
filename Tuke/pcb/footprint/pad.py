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

from Tuke.geo import Geo,Polygon

class Pad:
    """Defines a pad"""

    def __init__(self,id,a,b,thickness,clearance,mask):
        """Create a pad.

        id - Id name
        a - First point of line segment
        b - Second point
        thickness - Width of metal surrounding line segment
        clearance - Separation of pad from other conductors
        mask - Width of solder mask relief
        """

        self.id = id
        self.a = a
        self.b = b
        self.thickness = thickness
        self.clearance = clearance
        self.mask = mask

        pass

    def from_ab(self,thickness,id='../',layer=None):
        """Returns a box generated from a,b with a given thickness.

        For makng pads, clearances etc.
        """

        return Polygon(((self.a[0] - thickness,self.a[1] - thickness),
            (self.b[0] + thickness,self.b[1] - thickness),
            (self.b[0] + thickness,self.b[1] + thickness),
            (self.a[0] - thickness,self.a[1] + thickness)),id=id,layer=layer)

    def geo(self):
        """Generate geometry"""

        g = Geo()

        g.add(self.from_ab(self.thickness,id=self.id,layer='top.pad'))
        g.add(self.from_ab(self.thickness + (self.clearance * 2),layer='top.clearance'))
        g.add(self.from_ab(self.mask,layer='top.mask'))

        return g
