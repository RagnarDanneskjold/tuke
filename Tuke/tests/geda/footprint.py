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
from Tuke.geda import Footprint

class GedaFootprintTest(TestCase):
    """Perform tests of the geda.Footprint class"""

    def testGedaFootprint(self):
        """geda.Footprint"""

        common.load_dataset('geda_footprints')

        f = Footprint(common.tmpd + '/plcc4-rgb-led',Id('plcc4'))
        f = Footprint(common.tmpd + '/supercap_20mm',Id('supercap'))
