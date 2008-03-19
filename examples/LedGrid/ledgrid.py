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
from Tuke.geometry import translate,V
from Tuke.sch import Component,Pin,Symbol
from Tuke.library.footprint import Dil

class Led(Symbol):
    def _init(self):
        self.add(Dil(n=2))

        self.create_linked_pins(('anode','cathode'))

class LedGrid(Component):
    __required__ = ('rows','cols')
    __defaults__ = {'spacing':0.5}
    __version__ = (0,0)
    __baseversion__ = (0,0)
    def _init(self):
        top_leds = []
        bottom_leds = []

        for x in xrange(self.cols):
            prev = None
            for y in xrange(self.rows):
                l = Led(id=Id('LED%s_%s' % (str(x),str(y))))
                translate(l,V((x * self.spacing) - ((self.cols - 1) * self.spacing / 2),(y * self.spacing) - ((self.rows - 1) * self.spacing / 2)))
                l = self.add(l)

                if not prev:
                    top_leds.append(l)
                else:
                    l.connects.add(Id('../') + prev.id + 'cathode')

                prev = l

            bottom_leds.append(prev)

        # Link common anodes and cathodes
        for t in top_leds:
            t.anode.connects.add('../../anode')
        for b in bottom_leds:
            t.cathode.connects.add('../../cathode')
