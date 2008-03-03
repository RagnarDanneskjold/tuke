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
from Tuke.geometry import Line,ThinLine,V
from Tuke.geometry.line import make_line_vertexes

from math import sqrt

class GeometryLineTest(TestCase):
    """Perform tests of the geometry.Line/ThinLine class"""

    def test_make_line_vertexes(self):
        """geometry.line.make_line_vertexes()"""

        def T(a,b,thickness,segments,expected):
            v = make_line_vertexes(a,b,thickness,segments)
            self.assert_(common.vert_equal(v,expected))

        # horizontal
        T(V(0,0),V(1,0),1,2,
                (V(0,0.5),V(-0.5,0),V(0,-0.5),
                 V(1,-0.5),V(1.5,0),V(1,0.5)))

        T(V(1,0),V(0,0),1,2,
                (V(1,-0.5),V(1.5,0),V(1,+0.5),
                 V(0,+0.5),V(-0.5,0),V(0,-0.5)))

        # vertical
        T(V(0,0),V(0,1),1,2,
                (V(-0.5,0),V(0,-0.5),V(+0.5,0),
                 V(+0.5,1),V(0,+1.5),V(-0.5,1)))
        T(V(0,1),V(0,0),1,2,
                (V(+0.5,1),V(0,+1.5),V(-0.5,1),
                 V(-0.5,0),V(0,-0.5),V(+0.5,0)))

        # 45degree diag
        # width is set such that everything ends up on even multiples
        T(V(0,0),V(1,1),sqrt(1+1),2,
                (V(-0.5,+0.5),V(-0.5,-0.5),V(+0.5,-0.5),
                 V(+1.5,+0.5),V(+1.5,+1.5),V(+0.5,+1.5)))


        # point case should give a circle
        T(V(0,0),V(0,0),1,2,
                (V(+0.0,+0.5),V(-0.5,+0.0),V(+0.0,-0.5),
                 V(+0.0,-0.5),V(+0.5,+0.0),V(+0.0,+0.5)))

    def testLine(self):
        """geometry.Line"""

        p = Line(V(-1,2),V(3,4),0.234,layer='foo')
        self.assert_(p.render())

    def testThinLine(self):
        """geometry.ThinLine"""
        p = ThinLine(V(-10,2.5),V(34,4.3),2.2,layer='foo')
        self.assert_(p.render())
