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

from Tuke.geometry import Geometry,V,Transformation,Translation,translate,centerof

class ElementRefTest(TestCase):
    """Perform tests of the elementref module"""

    def testElementRef_wrap_returned(self):
        """ElementRef function return value wrapping"""

        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        class H:
            # Hide data from the bit manglers
            def __init__(self,hidden):
                self.hidden = hidden
            def __call__(self):
                return self.hidden

        class foo(Element):
            def r_id(self,id):
                return Id(id)
            def r_ref(self,base,id):
                return ElementRef(base(),Id(id))

        a = Element(id='a')
        a.add(foo(id='b'))

        T(a.b.r_id('..'),Id())
        T(a.b.r_id('bar'),Id('b/bar'))
        T(a.b.r_id('../../'),Id('..'))
        T(a.b.r_id('../b/'),Id('b'))

        T(a.b.r_ref(H(a.b._deref()),'..'),a['.'])
        T(a.b.r_ref(H(a.b._deref()),'.'),a.b)

        z = Element(id='z')
        T(a.b.r_ref(H(z),'.'),
                ElementRef(z,'.'))
