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
from Tuke import Id

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
