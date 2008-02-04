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

    def test_rndId(self):
        """rndId()"""

        self.assert_(isinstance(rndId(),Id))
        self.assert_(rndId() != rndId())
