#!/usr/bin/python
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


"""
Example Tuke-using program to generate an led grid.

Usage:

led_grid rows cols

Generates a series-parallel grid of leds and prints the resulting XML to
stdout.
"""

from Tuke import Id
from Tuke.units import MIL
from Tuke.geometry import translate,V,centerof
from Tuke.sch import Component,Pin,Symbol
from Tuke.library.footprint import Dil

from Tuke.pcb.trace import Trace
from Tuke.pcb import Point

class Led(Symbol):
    def _init(self):
        self.add(Dil(n=2))

        self.create_linked_pins(('anode','cathode'))

class LedGrid(Component):
    __required__ = ('rows','cols')
    __defaults__ = {'spacing':600 * MIL}
    __version__ = (0,0)
    __baseversion__ = (0,0)
    def _init(self):
        top_leds = []
        bottom_leds = []

        def dt(a,b):
            t = self.add(Trace(thickness=20 * MIL))
            t.set_endpoints(a,b)

        for x in xrange(self.cols):
            prev = None
            for y in xrange(self.rows):
                l = Led(id=Id('LED%s_%s' % (str(x),str(y))))
                translate(l,V((x * self.spacing) - ((self.cols - 1) * self.spacing / 2),
                              (y * self.spacing) - ((self.rows - 0) * self.spacing / 2)))
                l = self.add(l)

                if prev is None:
                    top_leds.append(l)
                else:
                    dt(prev.footprint._2,l.footprint._1)

                prev = l

            bottom_leds.append(prev)

        # Create offset points for the common anodes and cathodes.
        top_points = []
        for t in top_leds:
            p = Point()
            translate(p,centerof(t.footprint._1) + V(0,-self.spacing / 2))
            p = self.add(p)
            dt(t.footprint._1,p)
            top_points.append(p)
        bottom_points = []
        for t in bottom_leds:
            p = Point()
            translate(p,centerof(t.footprint._2) + V(0,self.spacing / 2))
            p = self.add(p)
            dt(t.footprint._2,p)
            bottom_points.append(p)

        # Link common anodes and cathodes
        p = None
        for i in top_points:
            if p is not None:
                dt(p,i)
            p = i
        p = None
        for i in bottom_points:
            if p is not None:
                dt(p,i)
            p = i 
