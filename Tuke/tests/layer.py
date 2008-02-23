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

import common

from unittest import TestCase
import Tuke
from Tuke import Layer

class LayerTest(TestCase):
    """Perform tests of the Layer module"""

    def testLayerInLayer(self):
        """Layer in operator"""

        def T(x):
            self.assert_(x)

        T(Layer('foo') in Layer('foo'))
        T(Layer('foo') in Layer('*'))
        T(Layer('*') in Layer('foo'))
        T(not Layer('foo.bar') in Layer('foo'))
        T(Layer('foo.bar') in Layer('foo.*'))
        T(Layer('*.foo') in Layer('bar.*'))
        T(not Layer('*.foo') in Layer('goo.bar.foo'))
        T(eval(repr(Layer('*.foo.*'))) == Layer('*.foo.*'))

    def testLayerRaises(self):
        """Layer handles invalid arguments"""

        self.assertRaises(TypeError,Layer,1)
        self.assertRaises(TypeError,Layer,None)
        self.assertRaises(ValueError,Layer,'...')
        self.assertRaises(ValueError,Layer,'.b.b.')
        self.assertRaises(ValueError,Layer,'.b*.b.')
