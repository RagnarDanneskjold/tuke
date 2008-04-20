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

import common

from unittest import TestCase
import Tuke.repr_helper

class repr_helperTest(TestCase):
    """Perform tests of repr_helper"""

    def testrepr_helper(self):
        """repr_helper decorator"""
        def T(got,expected = True):
            self.assert_(got == expected,'got: %s  expected: %s' % (got,expected))

        class foo:
            def __init__(self,a,b,bar,goo = 'green',zoo = 'sydney'):
                self.a = a
                self.b = b
                self.bar = bar
                self.goo = goo
                self.zoo = zoo

            @Tuke.repr_helper.repr_helper
            def __repr__(self):
                return ((self.a,self.b,self.bar),{'goo':self.goo,'zoo':self.zoo})

        
        f = foo(1,2,'werd')

        T(repr(f),"Tuke.tests.repr_helper.foo(1,2,'werd',goo='green',zoo='sydney')")

    def testnon_evalable_repr_helper(self):
        """non_evalable_repr_helper decorator"""
        class foo(object):
            def __init__(self,kw):
                self.kw = kw
            @Tuke.repr_helper.non_evalable_repr_helper
            def __repr__(self):
                return self.kw 

        # not gonna bother actually checking this, bah, pattern matching
        repr(foo({'frob':1}))
        repr(foo({'frob':1,'gob':'2'}))

    def testnon_evalable_repr_helper_nested_classes(self):
        """non_evalable_repr_helper with nested classes"""
        class foo(object):
            def __init__(self,kw):
                self.kw = kw
            @Tuke.repr_helper.non_evalable_repr_helper
            def __repr__(self):
                return self.kw

        class bar(foo):
            pass

        repr(bar({'frob':1}))
        repr(bar({'frob':1,'gob':'2'}))
