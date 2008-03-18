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
from Tuke import Element,Id,rndId,Connects

class ConnectsTest(TestCase):
    """Perform tests of the Connects module"""

    def testConnects(self):
        """Connects class"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))
        def R(ex,fn):
            self.assertRaises(ex,fn)

        a = Element('a')
        T(a.connects,set())

        b = Element('b')
        R(TypeError,lambda: a.connects.add(b))

        a.add(b)
        a.add(Element('c'))

        a.connects.add(a.b)

        T(a.b in a.connects)
        T(Id('b') in a.connects)
        T('b' in a.connects)
        T(not ('c' in a.connects))
        T(not (a.c in a.connects))

        R(TypeError,lambda: b in a.connects)
