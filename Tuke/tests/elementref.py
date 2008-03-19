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
from Tuke import Element,ElementRef,ElementRefError,Id,rndId

from Tuke.geometry import Geometry,V,Transformation,Translation,translate,Rotation,rotate,scale,centerof

from math import pi

class ElementRefTest(TestCase):
    """Perform tests of the elementref module"""

    def testElementRef_wrap_data_out(self):
        """ElementRef data out wrapping"""


        # This tests both wrapping bound functions, and plain attributes at the
        # same time.

        class H:
            # Hide data from the bit manglers
            def __init__(self,hidden):
                self.hidden = hidden
            def __call__(self):
                return self.hidden

        def T(elem, # element
              data_in, # data in
              expected = True): # data expected out
            got_fn = elem.fn(H(data_in)) 
            got_attr = elem.attr 
            self.assert_(expected == got_fn,
                    'got_fn: %s  expected: %s' % (got_fn,expected))
            self.assert_(expected == got_attr,
                    'got_attr: %s  expected: %s' % (got_attr,expected))


        class foo(Element):
            def fn(self,v):
                self.attr = v()
                return self.attr 

        a = Element(id='a')
        a.add(foo(id='b'))

        # Ids
        T(a.b,Id('..'),Id())
        T(a.b,Id('bar'),Id('b/bar'))
        T(a.b,Id('../../'),Id('..'))
        T(a.b,Id('../b/'),Id('b'))

        # Ref's with common bases
        T(a.b,ElementRef(a.b._deref(),'..'),a['.'])
        T(a.b,ElementRef(a.b._deref(),'.'),a.b)

        # Aliens
        z = Element(id='z')
        T(a.b,ElementRef(z,'.'),ElementRef(z,'.'))

        # Geometry
        def T(elem, # element
              data_in, # data in
              expected = True): # data expected out
            got_fn = elem.fn(H(data_in)) 
            got_attr = elem.attr
            expected = expected.round(5)
            got_fn = got_fn.round(5)
            got_attr = got_attr.round(5)
            self.assert_((expected == got_fn).all(),
                    'got_fn: %s  expected: %s' % (got_fn,expected))
            self.assert_((expected == got_attr).all(),
                    'got_attr: %s  expected: %s' % (got_attr,expected))

        # Vertexes
        T(a.b,V(1,2),V(1,2))
        with a.b as b:
            translate(b,V(-2,3))
        T(a.b,V(1,2),V(-1,5))

        # Transformations
        T(a.b,Translation(V(4,4)),Translation(V(4,4)))
        translate(a,V(-4,-4))
        T(a.b,Translation(V(4,4)),Translation(V(0,0)))

        # Verify that .transforms are applied in the correct order
        a = foo(id='a')
        rotate(a,pi / 2)
        b = foo(id='b')
        translate(b,V(1,2))
        a.add(b)

        T(a.b,V(1,2),V(4,-2))
        T(a.b,Translation(V(1,2)),Rotation(pi / 2) * Translation(V(1,2)))
