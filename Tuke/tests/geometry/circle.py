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

from Tuke.tests import common

from unittest import TestCase

from Tuke import Id
from Tuke.geometry import Circle,V

from Tuke.geometry.circle import arc_points

from math import pi,cos,sin,radians

class GeometryCircleTest(TestCase):
    """Perform tests of the geometry.Circle class"""

    def testGeometryCircle_arc_points(self):
        """arc_points() utility function"""

        def T(a,b):
            self.assert_(common.vert_equal(a,b))
        def F(a,b):
            self.assert_(not common.vert_equal(a,b))

        # test arc_points() finally
        T(arc_points(0,pi,1,1),
                (V(1,0),V(-1,0)))
        T(arc_points(pi,0,1,1),
                (V(-1,0),V(1,0)))

        # three points, note rotation is always anti-clockwise
        T(arc_points(0,pi,1,2),
                (V(1,0),V(0,1),V(-1,0)))
        T(arc_points(pi,0,1,2),
                (V(-1,0),V(0,-1),V(1,0)))

        # full circle
        T(arc_points(0,2*pi,1,4),
                (V(1,0),V(0,1),V(-1,0),V(0,-1),V(1,0)))
        T(arc_points(2*pi,0,1,4), # note same result as above
                (V(1,0),V(0,1),V(-1,0),V(0,-1),V(1,0)))

        T(arc_points(pi / 2,pi*1.5,0.5,4),
                (V(0,0.5),
                 V(-cos(radians(45))/2,sin(radians(45))/2),
                 V(-0.5,0),
                 V(-cos(radians(45))/2,-sin(radians(45))/2),
                 V(0,-0.5)))

    def testGeometryCircle(self):
        """geometry.Circle()"""

        a = Circle(dia=2,layer='foo')
        a = Circle(dia=1,layer='foo')
