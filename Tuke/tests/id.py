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
from Tuke import Id,rndId

class IdTest(TestCase):
    """Perform tests of the id module"""

    def testId(self):
        """Id class"""

        # normalization rules
        self.assert_(str(Id('')) == '.')
        self.assert_(str(Id('./')) == '.')
        self.assert_(str(Id('././')) == '.')

        self.assert_(str(Id('foo')) == 'foo')
        self.assert_(str(Id('foo/')) == 'foo')
        self.assert_(str(Id('foo/.')) == 'foo')
        self.assert_(str(Id('foo/./')) == 'foo')
        self.assert_(str(Id('foo/././')) == 'foo')

        self.assert_(str(Id('./foo')) == 'foo')
        self.assert_(str(Id('././foo')) == 'foo')
        self.assert_(str(Id('./././foo')) == 'foo')

        self.assert_(str(Id('../foo')) == '../foo')
        self.assert_(str(Id('../../foo')) == '../../foo')
        self.assert_(str(Id('../../../foo')) == '../../../foo')


        self.assert_(str(Id('./../foo')) == '../foo')
        self.assert_(str(Id('./../foo/..')) == '..')
        self.assert_(str(Id('./../foo/../.')) == '..')

        self.assert_(str(Id('/////')) == '.')
        self.assert_(str(Id('//..///')) == '..')
        self.assert_(str(Id('//..//../')) == '../..')


        # adding paths together
        self.assert_(str(Id('') + Id('')) == '.')
        self.assert_(str(Id('foo') + Id('')) == 'foo')
        self.assert_(str(Id('') + Id('foo')) == 'foo')
        self.assert_(str(Id('foo') + Id('bar')) == 'foo/bar')
        self.assert_(str(Id('foo') + Id('..')) == '.')
        self.assert_(str(Id('..') + Id('bar')) == '../bar')

        # Adding strings to Id's
        self.assert_(Id('foo') + 'bar' == Id('foo/bar'))

    def testIdAddSide_effects(self):
        """Id() + Id() has no side effects"""

        a = Id('foo')
        b = Id('bar')

        c = a + b

        self.assert_(str(a) == 'foo')
        self.assert_(str(b) == 'bar')
        self.assert_(str(c) == 'foo/bar')

    def testIdEqNeq(self):
        """Id() ==, != operators"""

        self.assert_(Id() == Id())
        self.assert_(not Id() != Id())

        self.assert_(Id('asdf') != Id())
        self.assert_(Id('asdf') == Id() + Id('asdf'))

    def testIdReprEval(self):
        """eval(repr(Id()))"""

        a = Id('bar')

        self.assert_(a == eval(repr(a)))

    def testIdHashable(self):
        """hash(Id())"""

        a = Id('foo')
        b = Id('bar')
        c = Id('foo')

        self.assert_(hash(a) == hash(c))
        self.assert_(hash(a) != hash(b))

    def testId__getitem__(self):
        """Id.__getitem__"""

        a = Id('a/b/c/d')

        def T(x):
            self.assert_(x)

        T(isinstance(a[0],Id))
        T(isinstance(a[0:3],Id))

        T(a[0] == 'a')
        T(a[1] == 'b')
        T(a[2] == 'c')
        T(a[3] == 'd')

        T(a[-1] == 'd')

        self.assertRaises(IndexError,a.__getitem__,4) 

        T(a[0:2] == 'a/b')
        T(a[2:0] == '.')
        T(a[2:0:-1] == 'c/b') # useless? who knows
        T(a[-2:] == 'c/d')

    def testIdInitWithId(self):
        """Id(Id('foo'))"""

        a = Id('foo')

        b = Id(a)

        self.assert_(hash(a) == hash(b))

        # Must not implement the simple self.id = other.id, as other.id may
        # change.
        self.assert_(id(a.id) != id(b.id))

    def testIdRaisesTypeErrors(self):
        """Id(1) raises TypeError"""

        self.assertRaises(TypeError,lambda x: Id(x),1)
        self.assertRaises(TypeError,lambda x: Id() + x,1)

    def test_rndId(self):
        """rndId()"""

        self.assert_(isinstance(rndId(),Id))
        self.assert_(rndId() != rndId())
