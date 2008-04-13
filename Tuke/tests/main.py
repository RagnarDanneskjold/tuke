# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
# (c) 2007,2008 Peter Todd <pete@petertodd.org>
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
from Tuke.main import *

class MainTest(TestCase):
    """Perform tests of the main module"""

    def testMain(self):
        """main() accepts -m"""

        common.load_dataset("check_dataset_not_empty1")

        main(["-m","test message"])
