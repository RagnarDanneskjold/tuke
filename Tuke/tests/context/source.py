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

from Tuke import Id,Element
from Tuke.geometry import Transformation,translate,Translation,V
from Tuke.context.source import Source,notify

import sys
import gc

class SourceTest(TestCase):
    def test_Source(self):
        """Source"""
        from Tuke.context.source import Source
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        s = Source(1,2,3)
        T(s.id,1)
        T(s.transform,2)
        T(s.parent,3)

        s.id = 10
        s.transform = 20
        s.parent = 30
        T(s.id,1)
        T(s.transform,2)
        T(s.parent,30)

    def test_Source_notify_raises(self):
        """Source notify raises exceptions on bad arguments"""

        class foo:
            pass

        a = Element(id=Id('a'))
        self.assertRaises(TypeError,
                lambda: notify(a,None,foo(),lambda:None))
        self.assertRaises(ValueError,lambda: notify(a,
            "Dr. Williams' Pink Pills for Pale People",foo(),lambda:None))
        self.assertRaises(TypeError,lambda: notify(a,'transform',object(),lambda:None))
        self.assertRaises(TypeError,lambda: notify(a,'transform',foo(),None))

    def test_Source_notify(self):
        """Source notify"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        a = Element(id=Id('a'))

        # Callable with a single value that is incremented on each call
        class v:
            def __init__(self):
                self.v = 0
            def __call__(self,closure):
                self.v += 1
                self.closure = closure 

        # Simple triggering of callbacks 
        vparent = v()
        notify(a,'parent',vparent,vparent)
        vtransform = v()
        notify(a,'transform',vtransform,vtransform)

        translate(a,V(1,1))
        T(vparent.v,0)
        T(vtransform.v,1)
        T(vtransform.closure,vtransform)

        z = Element(id=Id('z'))
        z.add(a)
        T(vparent.v,1)
        T(vparent.v,1)
        T(vtransform.v,1)
        T(vtransform.closure,vtransform)

        del a
        del z
