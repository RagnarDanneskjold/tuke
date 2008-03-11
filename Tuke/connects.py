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

Connectivity betwene elements refers to the connections between elements that
don't fall under the standard parent/child graph. This is used to store the
netlist information and to make traces possible. From an Elements perspective
it can be connected either to other elements, or to an Id that may in the
future resolve to an accessible element.

Connectivity is stored per element, but cached globally for speed.
"""

# Global connectivity will be the most interesting feature to implement.
# Elements are always relative, you can always take an Element, maybe even some
# really big complex schematic/pcb etc, and add it as a subelement of another
# element. So the global connectivity has to refer purely to weakrefs.

# stupid recursive includes
import Tuke as T

class Connects(set):
    """Per-Element connectivity info.
   
    The Set of Elements an Element is connected too. The elements in the set
    are actually stored as ElementRefs, and may or may not be resolvable to
    actual elements.

    Utility functions are provided to access the global information on
    connected elements, such as finding the set of all elements that an element
    is connected too.
    """

    def __new__(cls,parent,iterable = ()):
        """Create connectivity info

        parent - Parent element
        iterable - Optional iterable to add.
        """
        self = set.__new__(cls) 

        assert isinstance(parent,T.element.Element)
        self.parent = parent

        for i in iterable:
            self.add(i)

        return self
