# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
# (c) 2008 Peter Todd <pete@petertodd.org>
#
# This program is made available under the GNU GPL version 3.0 or
# greater. See the accompanying file COPYING for details.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.

from unittest import TestCase

import Tuke.tests.common


import Tuke
from Tuke import Id
from Tuke.geometry import translate,Hole,Polygon,Transformation

class GeometrytransformTest(TestCase):
    """Perform tests of the geometry.transform"""

    def testGeometryTransformation(self):
        """Transformation class"""
        def T(x):
            self.assert_(x)

        a = Transformation(v = (1,0))
        b = Transformation(v = (2,3))

        T(a == a)
        T(a == Transformation(v = (1,0)))
        T(a != b)
        T(not a != a)
        T(not a != Transformation(v = (1,0)))

        T(a.v == (1,0))

        T(a + b == Transformation(v = (3,3)))

    def testGeometryTransformationCallable(self):
        """Transformation class objects are callable"""
        def T(x):
            self.assert_(x)

        T(Transformation(v = (1,0))((0,0)) == (1,0))
        T(Transformation(v = (1,0))((0,1)) == (1,1))

        T(Transformation(v = (1,0))(((0,1),(3,4))) == ((1,1),(4,4)))
        T(Transformation(v = (10,10)) \
            (((0,1),((3,4),(5,6)))) == (((10,11),((13,14),(15,16)))))
        T(Transformation(v = (10,10)) \
            (((0,1),[],[(3,4),(5,6)])) == (((10,11),[],[(13,14),(15,16)])))

        T(Transformation(v = (1,0))(()) == ())
        T(Transformation(v = (1,0))([]) == [])
        T(Transformation(v = (1,0))([(),()]) == [(),()])

    def testGeometrytranslate(self):
        """translate()"""

        a = Polygon(((0,0),(1,1),(1,0)),layer='front.solder')
        b = Hole(1)

        x = translate(a,(1,1))
        y = translate(b,(1,1))

        z = translate(x,(-1,-1))
