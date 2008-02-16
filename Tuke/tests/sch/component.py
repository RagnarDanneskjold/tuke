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

from Tuke import Id,Netlist
from Tuke.sch import Component,Pin

class SchComponentTest(TestCase):
    """Perform tests of the sch.Component class"""

    def testComponent(self):
        """Basic tests"""

        root = Component(pins=(Pin('a'),'b','c'))
        
        foo = Component(pins=('a','b','c'),id='foo')
        bar = Component(pins=('a','b','c'),id='bar')

        root.add(foo)
        root.add(bar)

        root.link(root.a,foo.a)
        root.link(root.b,foo.b)
        root.link(root.c,foo.c)

        root.link(root.a,root.bar.c)
        root.link(root.b,root.bar.b)
        root.link(root.c,root.bar.a)


        self.assert_(root.netlist ==
        Netlist(
            (Id('a'),Id('foo/a'), Id('bar/c')),
            (Id('b'), Id('foo/b'), Id('bar/b')),
            (Id('c'), Id('foo/c'), Id('bar/a')),
            id=Id('.')))


