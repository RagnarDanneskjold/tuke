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

import Tuke.tests.common

from unittest import TestCase

from Tuke import Id
from Tuke.geometry import Translate,Hole,Polygon

class GeometryTranslateTest(TestCase):
    """Perform tests of the geometry.Translate class"""

    def testGeometryTranslate(self):
        """Basic tests"""

        a = Polygon(((0,0),(1,1),(1,0)),layer='front.solder')
        b = Hole(1)

        x = Translate(a,(1,1))
        y = Translate(b,(1,1))

        z = Translate(x,(-1,-1))
