# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
# (c) 2008 Peter Todd <pete@petertodd.org>
#
# This program is made available under the GNU GPL version 3.0 or
# greater. See the accompanying file COPYING for details.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.

from __future__ import with_statement

from unittest import TestCase
import Tuke
from Tuke import Element,ElementRef,Id,rndId

class ElementRefTest(TestCase):
    """Perform tests of the elementref module"""

    def testElementRef(self):
        """ElementRef"""
        root = [None]
        def T(ref,expected_id,expected_magic):
            r = ElementRef(root[0],ref)
            r2 = ElementRef(root[0],ref)

            r = r()
            r2 = r2()
            # Deref must return same object. 
            self.assert_(r is r2)

            # Check that connects is updated
            if root[0] is not None:
                self.assert_(root[0].connects.to(r))

            self.assert_(r.id == expected_id,
                    'got id: %s  expected id: %s' % (r.id,expected_id))
            self.assert_(r.magic == expected_magic,
                    'got magic: %s  expected magic: %s' % (r.magic,expected_magic))

        def R(ref):
            r = ElementRef(root[0],ref)
            self.assertRaises(KeyError,lambda: r())

        a = Element(id=Id('a'))
        a.magic = 0

        b = Element(id=Id('b'))
        b.magic = 1
        a.add(b)

        c = Element(id=Id('c'))
        c.magic = 2
        a.b.add(c)

        z = Element(id=Id('z'))
        z.magic = 3
        z.add(a)
        y = Element(id=Id('y'))
        y.magic = 4
        z.add(y)

        # Try different roots
        for r in (a,a.b,a['.']):
            root[0] = r

            T(Id('a'),Id('a'),0)
            T(a,Id('a'),0)
            T(Id('a/b'),Id('a/b'),1)
            T(a.b,Id('a/b'),1)
            T(Id('a/b/c'),Id('a/b/c'),2)
            T(a.b.c,Id('a/b/c'),2)

            # ../

            T(Id('.'),Id('.'),3)
            T(Id('y'),Id('y'),4)


            # Check exceptions.
            R(Id('..'))
            R(Id('../../'))
            R(Id('a/z'))
            R(Id('a/b/c/d'))
