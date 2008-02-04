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
from Tuke.pcb.footprint import Pin 

class PcbFootprintPinTest(TestCase):
    """Perform tests of the pcb.footprint.Pin class"""

    def testPcbFootprintPin(self):
        """Basic tests"""

        a = Pin(1,1,1,1,id=Id('1'))
