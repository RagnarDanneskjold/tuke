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
    def __init__(self,id):
        Symbol.__init__(self,
                pins = (Pin('anode'),Pin('cathode')),
                footprint = Dil(n=2),
                id = id)

class LedGrid(Component):
    def __init__(self,rows,cols,spacing,id):
        Component.__init__(self,
                pins = (Pin('anode'),Pin('cathode')),
                id = id)

        top_leds = []
        bottom_leds = []

        for x in xrange(cols):
            prev = None
            for y in xrange(rows):
                l = Led(id=Id('LED%s_%s' % (str(x),str(y))))
                translate(l,V((x * spacing) - ((cols - 1) * spacing / 2),(y * spacing) - ((rows - 1) * spacing / 2)))
                l = self.add(l)

                if not prev:
                    top_leds.append(l)
                else:
                    self.link(prev.cathode,l.anode)

                prev = l

            bottom_leds.append(prev)

        # Link common anodes and cathodes
        for t in top_leds:
            self.link(self.anode,t.anode)
        for b in bottom_leds:
            self.link(self.cathode,b.cathode)
