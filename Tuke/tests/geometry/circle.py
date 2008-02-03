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
from Tuke.geometry import Circle 

from Tuke.geometry.circle import arc_points

from math import pi,cos,sin,radians

class GeometryCircleTest(TestCase):
    """Perform tests of the geometry.Circle class"""

    def testGeometryCircle_arc_points(self):
        """arc_points() utility function"""

        def vert_equal(a,b):
            """Utility function to check if two lists of vertexes are approximetely equal."""
            if len(a) != len(b):
                return False
            for v1,v2 in zip(a,b):
                if len(v1) != len(v2):
                    return False
                for x1,x2 in zip(v1,v2):
                    if not common.fcmp(x1,x2):
                        return False
            return True

        def T(a,b):
            self.assert_(vert_equal(a,b))
        def F(a,b):
            self.assert_(not vert_equal(a,b))

        # Test our new comparison function
        T(((0,0),(1,1)),((0,0),(1,1)))
        F(((1,0),(1,1)),((0,0),(1,1)))
        F(((0,0),(1,0)),((0,0),(1,1)))

        # extra items must fail
        F(((0,0),(1,0)),((0,0),(1,0),(1,1)))

        # as well as vertexes with odd numbers of elements
        F(((0,0),(1,0)),((0,0),(1,)))
        F(((0,0),(1,0)),((0,0),(1,1,1)))


        # test arc_points() finally
        T(arc_points(0,pi,1,1),
                ((1,0),(-1,0)))
        T(arc_points(pi,0,1,1),
                ((-1,0),(1,0)))

        # three points, note rotation is always anti-clockwise
        T(arc_points(0,pi,1,2),
                ((1,0),(0,1),(-1,0)))
        T(arc_points(pi,0,1,2),
                ((-1,0),(0,-1),(1,0)))

        # full circle
        T(arc_points(0,2*pi,1,4),
                ((1,0),(0,1),(-1,0),(0,-1),(1,0)))
        T(arc_points(2*pi,0,1,4), # note same result as above
                ((1,0),(0,1),(-1,0),(0,-1),(1,0)))

        T(arc_points(pi / 2,pi*1.5,0.5,4),
                ((0,0.5),
                 (-cos(radians(45))/2,sin(radians(45))/2),
                 (-0.5,0),
                 (-cos(radians(45))/2,-sin(radians(45))/2),
                 (0,-0.5)))

    def testGeometryHole(self):
        """Basic tests"""
