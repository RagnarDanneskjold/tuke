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

from Tuke.id import Id


class Net(set):
    """Helper class for Netlist
    
    When Netlist returns a set of connected nets, it needs some way of updating
    the the connectivity list should the Net be modified. Net encapsulates set
    and does these notifications.
    """

    __slots__ = ['netlist']

    def __init__(self,i,netlist):
        set.add(self,i)

        self.netlist = netlist

    def add(self,i):
        # Check for the easy case first, i hasn't been entered into the Netlist yet
        if not i in self.netlist:
            # Add i to ourselves
            set.add(self,i)

            # Set i's connectivity to the same set as ourself.
            self.netlist[i] = self
        else:
            # The tough case, i is already connected, so we'll have to update
            # the connectivity of every id it's connected too.

            self.update(self.netlist[i])

            for n in self.netlist[i]:
                self.netlist[n] = self

    def remove(self,i):
        # Remove from the set
        set.remove(self,i)

        # Update Netlist
        del self.netlist[i]

class Netlist(dict):
    """Net connectivity.
    
    A Netlist holds connectivity information describing what Elements are
    connected to what. The connectivity information is in the form of sets() of
    Id()

    Usage:

    n = Netlist()

    i1 = Id('1')
    i2 = Id('2')
    i3 = Id('3')

    n[i1].add(i2)
    n[i3].add(i2)

    i1 in n[i3] == True

    n[i1].remove(i3)

    for i in n[i3]
    """

    def __init__(*args,**kwargs):
        """Initialize

        id - Prepended to all Id()'s
        """
        self = args[0]

        if 'id' in kwargs:
            self.id = kwargs['id']
        else:
            self.id = Id()

        # Process net definitions
        for s in args[1:]:
            for n in s:
                # The s[0] keeps adding all the elements in the list to the
                # same net.
                self[s[0]].add(n)

    def __repr__(self):
        # Generate a list of unique Id sets
        #
        # FIXME: doesn't prune single-Id sets
        s = [frozenset(v) for v in self.itervalues()]
        s = set(s) # removes dups
    
        # Turn into tuples for nice printing
        s = [tuple(v) for v in s]

        r = 'Netlist('

        for v in s:
            r += repr(v) + ','

        r += 'id=%s)' % repr(self.id)

        return r

    def __getitem__(self,i):
        """Returns the nets i is connected to, including itself."""

        # Note that this auto creation semantic has no corresponding deletion,
        # so possibly Netlists could become cluttered with unused single Id
        # Nets
        if not self.has_key(i):
            self[i] = Net(i,self)

        return dict.__getitem__(self,i)

    def __contains__(self,i):
        """True if i is connected to more than just itself."""
        if not self.has_key(i):
            return False
        else:
            if self[i] == set((i,)):
                return False
            else:
                return True
