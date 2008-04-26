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
import Tuke
from Tuke import Id,rndId,Element

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

        self.assert_(str(Id('foo/../')) == '.')
        self.assert_(str(Id('foo/../../')) == '..')
        self.assert_(str(Id('foo/../../bar')) == '../bar')
        self.assert_(str(Id('foo/.././../bar')) == '../bar')

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

    def testIdValidityChecking(self):
        """Id checks for invalid ids"""

        def T(str):
            self.assert_(isinstance(Id(str),Id))

        def F(str):
            self.assertRaises(ValueError,lambda:Id(str))

        T('_')
        T('__')
        T('.')
        T('..')
        T('_1234')
        T('')

        F('...')
        F('_12 3')
        F('_%')
        F('%')
        F('1')
        F('12')
        
    def testIdrelto(self):
        def T(id,base,expected = True):
            got = Id(id).relto(base)
            self.assert_(got == expected,'got: %s expected: %s' % (got,expected))

        # One or the other empty
        T('a','','a')
        T('','a','..')
        T('','a/b','../../')

        # Common parts
        T('a','','a')
        T('a','a','.')
        T('a/b','a','b')
        T('a/b/c/d','a/b/','c/d')
        T('../a/b/c/d','../a/b/','c/d')

        # No common parts
        T('b','a','../b')
        T('../b','a','../../b')
        T('../b','a/b','../../../b')

    def testId_len(self):
        """len(Id)"""

        def T(x):
            self.assert_(x)

        T(len(Id('_1/_2/_3')) == 3)
        T(len(Id('_1/_2')) == 2)
        T(len(Id('_1')) == 1)
        T(len(Id('.')) == 0)
        T(len(Id()) == 0)

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

        # Why the aa? At one point a subtle bug was present that wasn't being
        # caught with single character path elements.
        a = Id('aa/b/c/d')

        def T(x):
            self.assert_(x)

        T(isinstance(a[0],Id))
        T(isinstance(a[0:3],Id))

        T(a[0] == 'aa')
        T(a[1] == 'b')
        T(a[2] == 'c')
        T(a[3] == 'd')

        T(a[-1] == 'd')

        self.assertRaises(IndexError,a.__getitem__,4) 

        T(a[0:2] == 'aa/b')
        T(a[2:0] == '.')
        T(a[2:0:-1] == 'c/b') # useless? who knows
        T(a[-2:] == 'c/d')

    def testId__cmp__(self):
        """Id comparisons"""

        def T(x):
            self.assert_(x)

        T(Id('a') < Id('b'))
        T(not Id('a') > Id('b'))

        T(Id('b') > Id('a'))
        T(not Id('b') < Id('a'))

        T(Id('a/b') > Id('b'))
        T(not Id('a/b') < Id('b'))

        T(Id() < Id('a'))
        T(not (Id() > Id('a')))

    def testId__iter__(self):
        p = []

        for i in Id('aa/b/cc/dd'):
            self.assert_(isinstance(i,Id)) 
            p.append(i)

        self.assert_(p == [Id('aa'),Id('b'),Id('cc'),Id('dd')])

    def testIdInitWithId(self):
        """Id(Id('foo'))"""

        a = Id('foo')

        b = Id(a)

        self.assert_(hash(a) == hash(b))

    def testIdRaisesTypeErrors(self):
        """Id(1) raises TypeError"""

        self.assertRaises(TypeError,lambda x: Id(x),1)
        self.assertRaises(TypeError,lambda x: Id() + x,1)

    def testId_build_context(self):
        """Id._build_context()"""

        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        T(Id('spam')._build_context(Id('eggs'),False),Id('eggs/spam'))
        T(Id('spam')._build_context(Id('ham/eggs'),False),Id('ham/eggs/spam'))
        T(Id('spam')._build_context(Id('ham/eggs'),True),Id('ham'))

    def testId_apply_context(self):
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        class e(object):
            def __init__(self,id):
                self.id = Id(id)
                self._id_real = Id(id)

        T(Id()._apply_context(e('ham')),Id('ham'))
        T(Id('eggs')._apply_context(e('ham')),Id('ham/eggs'))
        T(Id('..')._apply_context(e('ham')),Id())

    def testId_remove_context(self):
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        class e(object):
            def __init__(self,id):
                self.id = id
                self._id_real = id

        T(Id()._remove_context(e('spam')),Id('..'))

        T(Id('ham')._remove_context(e('ham')),Id())
        T(Id('ham/eggs/spam')._remove_context(e('ham/eggs/spam')),Id())
        T(Id('ham/eggs')._remove_context(e('ham/eggs/spam')),Id('..'))

        T(Id('ham/eggs')._remove_context(e('Notary/Sojac')),Id('../../ham/eggs'))

        T(Id('..')._remove_context(e('../ham/eggs/spam')),Id('../../../'))

    def test_rndId(self):
        """rndId()"""

        self.assert_(isinstance(rndId(),Id))
        self.assert_(rndId() != rndId())
