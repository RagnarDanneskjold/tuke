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

        root.link(root.a,foo.a)
        root.link(root.b,foo.b)
        root.link(root.c,foo.c)

        root.link(root.a,root.bar.c)
        root.link(root.b,root.bar.b)
        root.link(root.c,root.bar.a)

        root.link(root.a,root.bar.moo.a)

        T(root.netlist,
            Netlist(
                (Id('a'),Id('foo/a'), Id('bar/c'), Id('bar/moo/a')),
                (Id('b'), Id('foo/b'), Id('bar/b')),
                (Id('c'), Id('foo/c'), Id('bar/a')),
                id=Id('.')))

    def testComponentLinksNonePins(self):
        """obj.link(None,None) fails"""

        root = Component(pins=(Pin('a'),'b','c'))
        root2 = Component(pins=(Pin('a'),'b','c'))

        self.assertRaises(TypeError,
                lambda x: x.link(x.a,None),root)

        self.assertRaises(TypeError,
                lambda x: x.link(x.a,root2),root)
