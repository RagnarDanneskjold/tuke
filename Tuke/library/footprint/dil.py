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

from Tuke.units import *
from Tuke.pcb import Footprint,Pin
from Tuke.geometry import translate,V

class Dil(Footprint):
    """Define a dual-inline package footprint.

    n - number of pins
    width - package width
    spacing - pin spacing
    pad - pad thickness
    drill - drill size
    clearance - width of clearance from the pin pad
    mask - diameter of the mask, independent of other values
    """
    __required__ = ('n',)
    __defaults__ = {'width':300 * MIL,
                    'spacing':100 * MIL,
                    'pad':16 * MIL,
                    'drill':28 * MIL,
                    'clearance':10 * MIL,
                    'mask':60 * MIL}

    def _init(self):
        assert not self.n % 2

        # Generate the pins
        for i in xrange(self.n):
            square = False
            if i == 0:
                square = True

            p = Pin(dia=self.drill,
                    thickness=self.pad,
                    clearance=self.clearance,
                    mask=self.mask,
                    square=square,
                    id='_' + str(i + 1))


            x = None
            y = None
            height = (self.n / 2) * self.spacing
            if i < self.n / 2:
                x = -(self.width / 2)
                y = (-i * self.spacing) + (height / 2) - self.spacing / 2
            else:
                x = self.width / 2
                y = -((-(i - self.n / 2) * self.spacing) + (height / 2) - self.spacing / 2)

            translate(p,V(x,y))

            self.add(p)
