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

from Tuke import Id,SingleElement
from Tuke.sch import Component,Pin

class SchComponentTest(TestCase):
    """Perform tests of the sch.Component class"""

    def testComponent(self):
        """Basic tests"""

        def T(got,expected):
            self.assert_(got == expected,'\ngot: %s\nexpected: %s' % (repr(got),repr(expected)))

        root = Component(pins=(Pin('a'),'b','c'))
        
        foo = Component(pins=('a','b','c'),id='foo')
        bar = Component(pins=('a','b','c'),id='bar')
        moo = Component(pins=('a','b','c'),id='moo')

        single = SingleElement(id='single')

        foo = root.add(foo)
        single = root.add(single)
        bar = root.add(bar)

        moo = bar.add(moo)
