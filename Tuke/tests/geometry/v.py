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
from Tuke import Element,Id
from Tuke.geometry import Translation,translate,rotate,V 

from Tuke.context.wrapper import unwrap

from math import pi

from numpy import matrix

class VTest(TestCase):
    """Perform tests of the v module"""

    def testV(self):
        """V class"""
        def T(x):
            self.assert_(x)

        v = V(5,6.6)
        T((v == V(5,6.6)).all())

        T((v + v == V(10,13.2)).all())

    def test_apply_remove_context(self):
        """V._(apply|remove)_context"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        a = Element(id=Id('a')) 
        b = Element(id=Id('b'))
        a.add(b)
        c = Element(id=Id('c'))
        a.b.add(c)

        a.v = V(1,1)
        c.v = V(1,1)

        translate(a.b,V(0,1))
        translate(a.b.c,V(1,0))

        T((a.b.c.v == V(2,2)).all())

        # The added d element here is important. It's transform is null, so any
        # optimizations that skip applying null transforms will hopefully
        # trigger bugs here.
        #
        # Secondly, if we used c, it still has a transform applied to any
        # results from it. For instance with a.b.c as uc, uc.v == V(2,1) right
        # now. Confusing!
        d = Element(id=Id('d'))
        a.b.c.add(d)
        with a.b.c.d as ud:
            # The original vertex is at 1,1 The two translations moved by
            # center point by 0,1 then 1,0 totaling 1,1 so the result cancels
            # out to 0,0
            T((ud[Id('../../')].v == V(0,0)).all())

        rotate(a,pi / 2)
        T(repr(a.b.c.v),repr(V(2,-2)))

        with a.b.c.d as ud:
            # Even with the rotation, the translates still cancel out, why?
            # Because the whole stack above a was rotated, which isn't "seen"
            # from the perspective of the stack above a.
            T((ud[Id('../../')].v == V(0,0)).all())

    def testVrepr(self):
        """repr(V)"""
        def T(v):
            v2 = eval(repr(v))
            self.assert_(isinstance(v2,V))
            self.assert_((v == v2).all())

        T(V(0,0))
        T(V(1,2))
        T(V(1.0,2))
        T(V(1.1,2))

    def testVslice(self):
        """V[] reprs to matrix"""

        v = V(5,6)

        vs = v[0:,0]

        self.assert_(repr(vs) == 'matrix([[ 5.]])') 
