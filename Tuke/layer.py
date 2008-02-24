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

from Tuke import repr_helper

class Layer(str):
    """Layer identifiers.

    Layout data is associated with layers that determine what part of the
    design the layout data is a part of. Layers are hierarchical, much the same
    way Ids are. However it doesn't make sense to refer to a previous layer the
    way it can in an Id, so the syntax is different.

    Example layer names:

    pcb.top.copper
    pcb.top.silk
    pcb.bottom.pad

    pcb.*.drill <- note glob usage

    sch.net <- for schematic drawings
    """

    def __init__(self,n):
        """Create a new Layer identifier"""
  
        if not isinstance(n,str):
            raise TypeError, 'Layer got %s, expected string' % type(n)

        bits = self.split('.')

        def T(x):
            if not x:
                raise ValueError, 'Invalid Layer identifier %s' % repr(n)

        for b in bits:
            T(b)
            T('*' not in b or b == '*')

        self = n

    def __contains__(self,other):
        if self == other:
            return True

        self = self.split('.')
        other = other.split('.')

        # Special case first, if self and other are of a different length, last
        # entry of the shorter must be * for contains to be true. The zip()
        # won't catch that due to it's truncated behavior.
        if len(self) != len(other):
            if len(self) < len(other):
                shorter = self
            else:
                shorter = other
            if '*' not in shorter[-1]:
                return False

        for (a,b) in zip(self,other):
            if a == b:
                continue

            if '*' in (a,b):
                continue

            return False

        return True

    @repr_helper
    def __repr__(self):
        return ((str(self),),None)
