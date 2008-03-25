# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
# (c) 2008 Peter Todd <pete@petertodd.org>
#
# This program is made available under the GNU GPL version 3.0 or
# greater. See the accompanying file COPYING for details.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.

from __future__ import with_statement

from unittest import TestCase

import Tuke.context as context

import sys
import gc

class SourceTest(TestCase):
    def test_Source(self):
        """Source"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        class ct(object):
            def __init__(self,v):
                self.v = v

        d = ct(42)
        class foo(object):
            bar = context.Source(d)
        T(foo.bar,d)

        # Make sure everything is transparent:
        f1 = foo()
        f2 = foo()
        T(f1.bar is d)
        T(f2.bar is d)

        n = ct('Evidence of a Baker')
        f1.bar = n 
        T(f1.bar is n)
        T(f2.bar is d)
        T(foo.bar is d)

        # Test a callback:
        c = ct('a day without yesterday')
        def fn(*args):
            c.v = args
        context.notify(f1,f1.bar,c,fn)

        T(c.v,'a day without yesterday')

        f1.bar = 'Creation'

        T(c.v,(c,))

        # A callback set before the first time the value was set
        f1 = foo()
        c = ct('The Salmon of Doubt')
        def fn(*args):
            c.v = args
        context.notify(f1,f1.bar,c,fn)

        T(c.v,'The Salmon of Doubt')

        f1.bar = 'Creation'

        T(c.v,(c,))

    def test_Source_for_memory_leaks(self):
        """Source does not leak memory"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        # The way callbacks are implemented could potentially leak memory, this
        # makes sure they don't.

        class foo(object):
            bar = context.Source(None)
        f = foo()

        d = 'ISBN 3936122202'
        baseline_ref_count = sys.getrefcount(d)

        f.bar = d
        f.bar = None
        T(sys.getrefcount(d),baseline_ref_count)

        f.bar = d
        del f
        T(sys.getrefcount(d),baseline_ref_count)
