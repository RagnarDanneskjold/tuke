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

    def testElementRef_wrap_data_in_out(self):
        """ElementRef data in/out wrapping"""


        # This tests both wrapping bound functions, and plain attributes at the
        # same time, in both directions at the same time. Two test vectors are
        # provided, the data in the outer context, and the inner version.  The
        # unwrapped data is then wrapped again when it's passed back to the
        # outer context, and checked that it matches. 

        class H:
            # Hide data from the bit manglers
            def __init__(self,hidden):
                self._hidden = hidden
            def __call__(self):
                return self._hidden

        def T(elem, # element
              data_in, # data in
              expected, # data expected in the wrapped context
              equiv_in=None): # equivilent representation to data_in
            if equiv_in is None:
                equiv_in = data_in
            got_fn = elem.fn(H(data_in),expected) 
            got_attr = elem.attr

            for i,o in (got_fn,got_attr):
                o = o._hidden
                self.assert_(expected == i and o == equiv_in,
                        '\ngot_fn: %s\ngot_attr: %s\nexpected: %s\ndata_in: %s' %
                                        ((got_fn[0],got_fn[1]._hidden),
                                         (got_attr[0],got_attr[1]._hidden),
                                         expected,data_in))


        class foo(Element):
            def fn(self,vh,v):
                self.attr = (vh(),H(v)) 
                return self.attr 

        a = Element(id='a')
        a.add(foo(id='b'))

        # Ids
        T(a.b,Id('..'),Id())
        T(a.b,Id('bar'),Id('b/bar'))
        T(a.b,Id('../../'),Id('..'))
        T(a.b,Id('../b/'),Id('b'),Id('.')) # note the equiv representation

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
            got_fn = elem.fn(H(data_in),expected)
            got_attr = elem.attr

            expected = expected.round(5)
            for i,o in (got_fn,got_attr):
                i = i.round(5)
                o = o._hidden.round(5)
                self.assert_((expected == i).all() and (o == data_in).all(),
                        '\ngot_fn: %s\ngot_attr: %s\nexpected: %s\ndata_in: %s' %
                                        ((got_fn[0],got_fn[1]._hidden),
                                         (got_attr[0],got_attr[1]._hidden),
                                         expected,data_in))

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
