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
from Tuke import srElement
from Tuke.geometry import V,translate,Transformation
from Tuke.geometry.util import *

class UtilTest(TestCase):
    """Perform tests of the geometry.util module"""

    def test_centerof(self):
        """centerof()"""

        def T(a,b):
            self.assert_((a == b).all())

        e = srElement()

        T(centerof(e),V(0,0))
        translate(e,V(1,2))
        T(centerof(e),V(1,2))

        self.assertRaises(TypeError,lambda: centerof(V(0,0)))
        self.assertRaises(TypeError,lambda: centerof(Transformation()))
        self.assertRaises(TypeError,lambda: centerof('asdf'))
