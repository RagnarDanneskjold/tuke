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
from Tuke.sch import Symbol,Pin

class SchSymbolTest(TestCase):
    """Perform tests of the sch.Symbol class"""

    def testSymbol(self):
        """Symbol class"""

        def T(got,expected=True):
            self.assert_(got == expected,'\ngot: %s\nexpected: %s' % (repr(got),repr(expected)))

        class foo(Symbol):
            def _init(self):
                a = Pin(id='a')
                b = Pin(id='b')
                c = Pin(id='c')
                self.create_linked_pins((a,b,c,'d'))

        f = foo()

        T(f.a.connects.to(Id('../footprint/_1')))
        T(f.b.connects.to(Id('../footprint/_2')))
        T(f.c.connects.to(Id('../footprint/_3')))
        T(f.d.connects.to(Id('../footprint/_4')))
