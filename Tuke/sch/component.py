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

from Tuke import Netlist,Element,Id

class Component(Element):
    """Defines a Component.
   
    Components are representations of electrical components in a schematic.
    They are meant to be subclassed by the actual schematic symbols who will
    provide a custom rendering.

    Components have a Netlist, describing the connectivity of pins within them.

    A component has pins, a dict of names that map to Id's Pins is shortened to
    p as you'll be doing a whole lot of connecting pins to pins.
    """

    def __init__(self,id=Id()):
        """Create a component.

        id - Id name
        """

        Element.__init__(self,id=id)

        self.netlist = Netlist(id=id)

        self.p = {}

    def define_pins(self,*names):
        """Define pins by name."""

        for n in names:
            self.p[n] = Id(n)
