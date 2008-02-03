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
from Tuke.geometry import Line,ThinLine 

class GeometryLineTest(TestCase):
    """Perform tests of the geometry.Line/ThinLine class"""

    def testGeometryHole(self):
        """Basic tests"""

        a = Line((0,0),(1,1),1,layer='foo')

        print a.render()

        print ThinLine((0,1),(0,1),2,layer='foo').render()
