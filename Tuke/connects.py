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

"""Element connectivity.

Connectivity between elements refers to the connections between elements that
don't fall under the standard parent/child graph. This is used to store the
netlist information and to make traces possible.

Connectivity comes in two types, explicit and implied. An explicit connection
is one that is stored in a Connects object in an Element. The implied
connection is the reverse of that explicit connection. An explicit connection
may be left dangling if there is no actual Element at the location that it's
ElementRef is pointing to. Implicit connections simply don't exist until the
corresponding explicit connection is made.

Connectivity is stored per Element, but cached globally for speed and to allow
for implicit connections.

"""

import Tuke

# Implicit connections will be the most interesting feature to implement.
# Elements are always relative, you can always take an Element, maybe even some
# really big complex schematic/pcb etc, and add it as a subelement of another
# element. To deal with that, the parent change hooks are used so that changes
# to the Element graph can be detected and the associated implicit connections
# updated.

class Connects(set):
    """Per-Element connectivity info.
   
    The Set of Elements an Element is connected too. The elements in the set
    are stored as ElementRefs, and may or may not be resolvable to actual
    elements.

    Utility functions are provided to access the global information on
    connected elements, such as finding the set of all Elements that an Element
    is connected too.
    """

    def __new__(cls,iterable = (),base = None):
        """Create connectivity info

        iterable - Optional iterable of Ids to add.
        base - Base element, may be set after initialization
        """
        self = set.__new__(cls) 

        assert isinstance(base,Tuke.Element)
        self.base = base 

        for i in iterable:
            self.add(Tuke.ElementRef(base,Tuke.Id(i)))

        return self

    def _make_ref(self,ref):
        # This is actually kinda clever. We're storing ElementRefs, and one
        # ElementRef is another ElementRef if their base and reference are
        # equal... So, test for that, and simply return the ref!
        try:
            if not (ref._base == self._base):
                raise ValueError, \
                    "Base Elements must match, got %s, need %s" % \
                            (ref._base,self._base)

            return ref
        except AttributeError:
            try:
                return Tuke.ElementRef(self._base,Tuke.Id(ref))
            except TypeError:
                raise TypeError, "Expected an Id, string, or ElementRef, not %s" % type(ref)
        

    def add(self,ref):
        """Add an explicit connection.

        ref - Element or Id
        """

        ref = self._make_ref(ref)
        super(self.__class__,self).add(ref)

    def __contains__(self,other):
        """True if there is an explicit connection from self to other"""
        ref = self._make_ref(other)
        return super(self.__class__,self).__contains__(ref)

    def _get_base(self):
        return self._base
    def _set_base(self,v):
        self._base = v
        for e in self:
            e._base = v
    base = property(_get_base,_set_base)

    @Tuke.repr_helper
    def __repr__(self):
        return (([r.id[1:] for r in self],),
                {})
