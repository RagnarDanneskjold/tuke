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
from Tuke import Element
from Tuke.geometry import V,Transformation,Translation,translate,Rotation,rotate,RotationAroundCenter,rotate_around_center,Scale,scale

from math import pi

class GeometrytransformTest(TestCase):
    """Perform tests of the geometry.transform"""

    def testGeometryTransformation(self):
        """Transformation class"""
        def T(x):
            self.assert_(x)

        a = Transformation()

        T((a(V(5,6.6)) == V(5,6.6)).all())

    def testGeometryTransformaton__repr__(self):
        """repr(Transformation)"""

        t = Transformation()
        self.assert_((eval(repr(t)) == t).all())

        self.assert_(repr(Transformation(((1,2),))) == 'matrix([[1, 2]])')

    def testGeometryTransformationCallable(self):
        return

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

        def T(i):
            self.assertRaises(TypeError,lambda x: Transformation()(x),i)
        T('asdf')
        T(None)
        T((None,))
        T((1,2,3))
        T(((1,1),((3,4),(),(lambda x: x,1))))

    def testGeometrytranslate(self):
        """translate, rotate, rotate_about_center"""

        def T(a,b,f,*args,**kwargs):
            """Element transform function test harness.

            Applies f(e,*args,**kwargs) to element e. Then applies e.transform
            to a and checks that the resulting vertex is == b.
            """

            e = Element()

            f(e,*args,**kwargs)

            # The repr()-based comparison seems to avoid floating point
            # "almost" equal errors.
            self.assert_(repr(e.transform(a)) == repr(b))

        T(V(2,3),V(5,-1),translate,V(3,-4))
        T(V(1,1),V(-1,-1),rotate,pi)
        T(V(-1,5),V(-2,15),scale,V(2,3))
        T(V(1,1),V(3,3),rotate_around_center,pi,V(2,2))
