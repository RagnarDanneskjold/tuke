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

    def link(self,a,b):
        """Connect pin a to pin b
        
        Both a and b must either be a pin on self, or a child of self.
        """

        # Note that a and b are simply Pin objects, we have to figure out where
        # they are by searching through our sub elements.

        def deref(i):
            # First case, valid Id's get passed on unchanged, so you can state
            # obj.link(self.Vcc,Id('../Vcc'))
            try:
                i = Id(i)
                return i
            except TypeError:
                # Must be from a Component pin. Find out which one.

                for p in self:
                    if p == i:
                        # One of our pins, return id unchanged.
                        return p.id

                # Look in sub-components

                # Need to keep track of what Id() level the search is at, hence
                # base.
                def add_subs_to_check(base,subs):
                    return [(base + s.id,s) for s in subs]

                # Depth first search, storing unchecked components in check
                check = add_subs_to_check(Id('.'),self.subs) 
                while check:
                    base,c = check.pop()
                    if isinstance(c,Component):
                        for p in c:
                            if p == i:
                                # Found, return with correct path.
                                return base + p.id
                    check += add_subs_to_check(base,c.subs)

            # Found nothing.

            # This is needed as we must return KeyError even if i is something
            # invalid, like None
            try:
                raise KeyError, 'Pin \'%s\' not found under \'%s\'' % (i.id,self.id)
            except AttributeError:
                raise KeyError, 'Not a valid pin'

        a = deref(a)
        b = deref(b)

        self.netlist[a].add(b)
