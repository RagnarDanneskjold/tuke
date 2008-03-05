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
from Tuke import repr_helper,non_evalable_repr_helper 

class repr_helperTest(TestCase):
    """Perform tests of repr_helper"""

    def testrepr_helper(self):
        """repr_helper decorator"""

        class foo:
            def __init__(self,a,b,goo = 'green'):
                self.a = a
                self.b = b
                self.goo = goo

            @repr_helper
            def __repr__(self):
                return ((self.a,self.b),{'goo':self.goo})

        
        f = foo(1,2)

        self.assert_(repr(f) == 'Tuke.tests.repr_helper.foo(1,2,goo = \'green\')')

    def testrepr_helper_class_name_override(self):
        """repr_helper class name override"""

        class foo:
            def __init__(self,a,b,goo = 'green'):
                self.a = a
                self.b = b
                self.goo = goo

            @repr_helper
            def __repr__(self):
                return ((self.a,self.b),{'goo':self.goo,'_repr_helper_class_name_override':'bar'})

        
        f = foo(1,2)
        self.assert_(repr(f) == 'Tuke.tests.repr_helper.bar(1,2,goo = \'green\')')

    def testnon_evalable_repr_helper(self):
        class foo(object):
            def __init__(self,kw):
                self.kw = kw
            @non_evalable_repr_helper
            def __repr__(self):
                return self.kw 

        # not gonna bother actually checking this, bah, pattern matching
        repr(foo({'frob':1}))
        repr(foo({'frob':1,'gob':'2'}))
