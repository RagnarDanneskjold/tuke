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
from Tuke import Element,srElement,Id,rndId,Connects

class ConnectsTest(TestCase):
    """Perform tests of the Connects module"""

    def testConnectsExplicit(self):
        """Explicit connections"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))
        def R(ex,fn):
            self.assertRaises(ex,fn)

        a = srElement('a')
        T(a.connects,set())

        b = srElement('b')
        R(TypeError,lambda: a.connects.add(b))

        a.add(b)
        a.add(srElement('c'))

        a.connects.add(a.b)

        T(a.b in a.connects)
        T(Id('b') in a.connects)
        T('b' in a.connects)
        T(not ('c' in a.connects))
        T(not (a.c in a.connects))

        R(TypeError,lambda: b in a.connects)

    def testConnectsImplicit(self):
        """Implicit connections"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))
        def R(ex,fn):
            self.assertRaises(ex,fn)


        # Basics
        a = srElement('a')
        a.add(srElement('b'))

        T(not a.b.connects.to('..'))
        a.connects.add(a.b)

        T(a.connects.to(a.b))
        T(a.b.connects.to('..'))


        # Parent change
        c = srElement('c')
        c.connects.add('..')
        c.connects.add('../b')

        T(c.connects.to('..'))
        T(c.connects.to('../b'))
        a.add(c)
        T(c.connects.to('..'))
        T(c.connects.to('../b'))

        T(a.connects.to(a.c))
        T(a.b.connects.to('../c'))

        # More complex parent changing
        a = srElement('a')
        b = srElement('b')
        c = srElement('c')

        c.connects.add('../../')

        b.add(c)
        a.add(b)
        T(a.connects.to('b/c'))

    def testConnectsReprEvalRepr(self):
        """repr(eval(repr(Connects))) round trip"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        a = srElement('a')
        a.add(srElement('b'))
        a.b.add(srElement('c'))
        a.connects.add('..')
        a.connects.add(a.b)
        a.connects.add(a.b.c)

        a2 = srElement('a')
        a2.connects = eval(repr(a.connects))
        a2.connects.base = a2
        T(repr(a2.connects),repr(a.connects))

    def testElementRemoveNotImplemented(self):
        """Element.remove() not yet implemented"""

        # This is a real test, if this fails, we need to make sure that
        # Connects handles the case where a Element parent is removed.
        a = srElement('a')
        self.assert_(not hasattr(a,'remove'))
