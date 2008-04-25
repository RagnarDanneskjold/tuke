# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
# (c) 2008 Peter Todd <pete@petertodd.org>
#
# This program is made available under the GNU GPL version 3.0 or
# greater. See the accompanying file COPYING for details.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.

import gc

import common

from unittest import TestCase
import Tuke
from Tuke import Element,Id,rndId,Connects

class ConnectsTest(TestCase):
    """Perform tests of the Connects module"""

    def testConnectsExplicit(self):
        """Explicit connections"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))
        def R(ex,fn):
            self.assertRaises(ex,fn)

        a = Element(id=Id('a'))
        T(set(a.connects),set())

        b = Element(id=Id('b'))
        R(ValueError,lambda: a.connects.add(b))

        a.add(b)
        a.add(Element(id=Id('c')))

        a.connects.add(a.b)

        T(a.b in a.connects)
        T(Id('a/b') in a.connects)
        T(not (Id('c') in a.connects))
        T(not (a.c in a.connects))

        R(ValueError,lambda: Element() in a.connects)

    def testConnectsImplicit(self):
        """Implicit connections"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))
        def R(ex,fn):
            self.assertRaises(ex,fn)

        # Implicit connections use a lot of weakref magic. That said, they
        # should function fine with, and without, the garbage collector
        # enabled.
        #
        # That said, until Element.remove is implemented, this can't be a
        # problem anyway.
        for i,gc_enabled in enumerate((False,False,False,True,True)):
            if gc_enabled:
                gc.enable()
            else:
                gc.disable()

            # Basics
            a = Element(id=Id('a'))
            a.add(Element(id=Id('b')))

            T(not a.b.connects.to(a))
            a.connects.add(a.b)

            T(a.connects.to(a.b))
            T(a.b.connects.to(a))

            # Parent change
            c = Element(id=Id('c'))
            c.connects.add(Id('.'))
            c.connects.add(Id('b'))

            T(c.connects.to(Id('.')))
            T(c.connects.to(Id('b')))
            a.add(c)
            T(a.c.connects.to(a))
            T(a.c.connects.to(a.b))

            T(a.connects.to(a.c))
            T(a.b.connects.to(a.c))

            # More complex parent changing
            a = Element(id=Id('a'))
            b = Element(id=Id('b'))
            c = Element(id=Id('c'))

            c.connects.add(Id('../'))

            b.add(c)
            a.add(b)
            T(a.connects.to(Id('a/b/c')))

        T(gc.isenabled())

    def testConnectsReprEvalRepr(self):
        """repr(eval(repr(Connects))) round trip"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        a = Element(id=Id('a'))
        a.add(Element(id=Id('b')))
        a.b.add(Element(id=Id('c')))
        a.connects.add(Id('.'))
        a.connects.add(a.b)
        a.connects.add(a.b.c)

        a2 = Element(id='a')
        a2.connects = eval(repr(a.connects))
        a2.connects.base = a2
        T(repr(a2.connects),repr(a.connects))

    def testElementRemoveNotImplemented(self):
        """Element.remove() not yet implemented"""

        # This is a real test, if this fails, we need to make sure that
        # Connects handles the case where a Element parent is removed.
        a = Element(id=Id('a'))
        self.assert_(not hasattr(a,'remove'))
