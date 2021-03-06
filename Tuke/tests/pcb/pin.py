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

from Tuke.pcb import Pin 

class PcbFootprintPinTest(TestCase):
    """Perform tests of the pcb.footprint.Pin class"""

    def testPcbFootprintPin(self):
        """Pin()"""

        a = Pin(dia=1,
                thickness=1,
                clearance=1,
                mask=1,
                id='_1')
