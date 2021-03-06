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
from Tuke.pcb import Pad 

class PcbFootprintPadTest(TestCase):
    """Perform tests of the pcb.footprint.Pad class"""

    def testPcbFootprintPad(self):
        """Pad()"""

        a = Pad(a=(0,0),b=(1,1),
                thickness=0.5,
                clearance=0.2,
                mask=0.6)
