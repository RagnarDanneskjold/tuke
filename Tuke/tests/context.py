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

class ContextTest(TestCase):
    """Perform tests of the context module"""

    def test_context_source(self):
        """context_source"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        class ct(object):
            def __init__(self,v):
                self.v = v

        d = ct(42)
        class foo(object):
            bar = context.context_source(d)
        T(foo.bar,d)

        # Make sure everything is transparent:
        f1 = foo()
        f2 = foo()
        T(f1.bar,d)
        T(f2.bar,d)

        n = ct('Evidence of a Baker')
        f1.bar = n 
        T(f1.bar,n)
        T(f2.bar,d)
        T(foo.bar,d)

        # Setup some callbacks:
        c = ct('a day without yesterday')
        def fn(*args):
            c.v = args
        context.notify(f1,f1.bar,c,fn)

        T(c.v,'a day without yesterday')

        f1.bar = ct('Creation')

        T(c.v,(c,))
