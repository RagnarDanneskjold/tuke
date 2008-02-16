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

from Tuke.sch.pin import Pin

class Component(Element):
    """Defines a Component.
   
    Components are representations of electrical components in a schematic.
    They are meant to be subclassed by the actual schematic symbols who will
    provide a custom rendering.

    Components have a Netlist, describing the connectivity of pins within them.

    A component has pins, which are defined by define_pins() A component can
    link() pins of itself, or sub components, together.

    Pin names must be valid python names, sutable for c.pin_name
    """

    def __init__(self,pins=(),id=Id()):
        """Create a component.

        pins - Pin list
        id - Id name
        """

        Element.__init__(self,id=id)

        self.netlist = Netlist(id=id)

        for p in pins:
            if not isinstance(p,Pin):
                p = Pin(p)
            self.add(p)

    def __getattr__(self,name):
        """Resolve references to pin names"""
        if Id(name) in [p.id for p in self.subs]:
            return (self,Id(name)) 
        else:
            raise AttributeError, name

    def link(self,a,b):
        """Connect pin a to pin b"""

        # Figure out correct Id paths for a and b

        def deref(i):
            # First case, already dereferenced Id's get passed on unchanged, so
            # you can state obj.link(self.Vcc,Id('../Vcc'))
            if isinstance(i,Id):
                return i 
            else:
                # Must be from a Component pin
                o,n = i

                # Is the object actually ourselves?
                if id(o) == id(self):
                    # Pass unchanged
                    return n
                else:
                    # Check that the object is one of our subclasses
                    assert(o in self.subs)

                    # Good, return with correct path
                    return o.id + n
    
        a = deref(a)
        b = deref(b)

        self.netlist[a].add(b)
