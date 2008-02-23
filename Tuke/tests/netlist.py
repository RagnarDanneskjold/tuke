# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
# (c) 2008 Peter Todd <pete@petertodd.org>
#
# This program is made available under the GNU GPL version 3.0 or
# greater. See the accompanying file COPYING for details.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.

import os
import shutil

import common

from unittest import TestCase
import Tuke
from Tuke import Id,rndId,Netlist

class NetlistTest(TestCase):
    """Perform tests of the netlist module"""

    def testNetlist(self):
        """Netlist class"""

        T = self.assert_
        F = lambda x: self.assert_(not x)

        T(True)
        F(False)

        n = Netlist()

        i1 = Id('1')
        i2 = Id('2')
        i3 = Id('3')
        i4 = Id('4')
        i5 = Id('5')


        # Nets are automagically created
        T(n[i1] == set((i1,)))

        # Backwards and forwards link in the simple case
        n[i1].add(i2)
        T(n[i1] == set((i1,i2)))
        T(n[i2] == set((i1,i2)))

        # Backwards and forwards link in the complex case
        n[i3].add(i4)
        n[i1].add(i4)
        T(n[i1] == set((i1,i2,i3,i4)))
        T(n[i2] == set((i1,i2,i3,i4)))

        # Id() in Netlist works
        T(i1 in n)
        F(i5 in n)
        T(n[i5] == set((i5,)))
        F(i5 in n)

        # Removal
        n[i1].remove(i3)
        T(n[i1] == set((i1,i2,i4)))
        T(n[i2] == set((i1,i2,i4)))
        F(i3 in n)

        # repr(Netlist)
        T(repr(eval(repr(n)) == repr(n)))
        n = Netlist()
        T(repr(eval(repr(n)) == repr(n)))
        n = Netlist(id=rndId())
        T(repr(eval(repr(n)) == repr(n)))


        # Netlist.upate()

        # Same Id() level
        n1 = Netlist((Id('1'),Id('2')),(Id('3'),Id('4')))
        n2 = Netlist((Id('2'),Id('3')),(Id('1'),Id('4')))
        n3 = Netlist((Id('1'),Id('2'),Id('3'),Id('4')))
        n2bak = repr(n2)

        n1.update(n2)

        T(repr(n2) == n2bak)
        T(repr(n1) == repr(n3))

        # Different Id() level
        n1 = Netlist()
        n2 = Netlist((Id('1'),Id('2')),(Id('3'),Id('4')),id=Id('a'))
        n3 = Netlist((Id('a/1'),Id('a/2')),(Id('a/3'),Id('a/4')))
   
        n1.update(n2)
        T(repr(n1) == repr(n3))
