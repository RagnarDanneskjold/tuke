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

from shapely.geometry import Polygon

class Pin:
    """Defines a pin"""

    def __init__(self,hole,thickness,clearance,mask,square=False):
        """Create a pin.

        
        """

        self.hole = hole
        self.thickness = thickness
        self.clearance = clearance
        self.mask = mask
        self.square = square

        pass

    def gen_pad_shape(self,thick,square):
        """Returns a pad shape, circle or square, with a given thickness.

        For makng pads or masks.
        """

        return Polygon(((-thick,-thick),(thick,-thick),(thick,thick),(-thick,thick)))

    def geo(self):
        """Generate geometry"""

        g = {}

        g['*.drill'] = (((0,0),self.hole),)

        g['top.pad'] = (self.gen_pad_shape(self.thickness,self.square),)
        g['top.mask'] = (self.gen_pad_shape(self.mask,self.square),)

        g['top.clearance'] = (self.gen_pad_shape(self.mask + (self.clearance * 2),self.square),)

        return g
