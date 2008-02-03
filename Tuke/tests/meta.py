# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
# (c) 2007 Peter Todd <pete@petertodd.org>
#
# This program is made available under the GNU GPL version 3.0 or
# greater. See the accompanying file COPYING for details.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.

import common
import os
import math

from unittest import TestCase

class MetaTest(TestCase):
    """Perform meta testing of the test suite"""

    def testLoadDatasetInvalid(self):
        """load_dataset() with invalid dataset should fail immediately"""

        self.assertRaises(AssertionError,common.load_dataset,"invalid dataset")

        # make sure the above didn't clobber further tests 
        common.load_dataset('empty')

    def testCheckDataset(self):
        """check_dataset()"""

        def check(a,b):
            common.load_dataset(a)
            return common.check_dataset(b)

        def t(a,b):
            self.assert_(check(a,b))

        def f(a,b):
            self.assert_(not check(a,b))

        t("empty","empty")
        f("empty","check_dataset_not_empty1")
        t("check_dataset_not_empty1","check_dataset_not_empty1")
        f("check_dataset_not_empty1","check_dataset_not_empty2")
        f("check_dataset_not_empty1","check_dataset_not_empty3")
        f("check_dataset_not_empty1","check_dataset_not_empty4")
        t("check_dataset_not_empty4","check_dataset_not_empty4")

    def testCheckDatasetSymlinks(self):
        """check_dataset() knows about symlinks"""

        common.load_dataset('check_dataset_not_empty_symlink')

        # Create a symlink
        os.symlink(common.tmpd + "/foo",common.tmpd + "/bar")

        self.assert_(not common.check_dataset('check_dataset_not_empty_symlink.check'))


    def testFcmp(self):
        """fcmp() floating point comparison function"""

        def T(obs,exp,eps=None):
            if eps:
                self.assert_(common.fcmp(obs,exp,eps))
            else:
                self.assert_(common.fcmp(obs,exp))

        def F(obs,exp,eps=None):
            if eps:
                self.assert_(not common.fcmp(obs,exp,eps))
            else:
                self.assert_(not common.fcmp(obs,exp))

        # really basic stuff
        T(0.0,0.0)
        T(1,1)
        T(0.1,0.1)
        T(math.pi,math.pi)

        F(0,1)
        F(1,1.1)

        # relative comparisons
        T(math.pi,math.pi - 1e-6,1e-6) # note scaling, this isn't a close non-match
        F(math.pi,math.pi - (1e-6 * math.pi * 2),1e-6) # scaling applied

        # trigger absolute comparisons of very small numbers
        T(0.01,0,0.1)
        F(0.1,0,0.1)

        # some funny cases
        T(0,1,1)
        T(0,100000000,1) # yup, correct too, scaling is as a percentage, so anything will match

        # signed
        T(-0,0)
        F(-1,1)
        F(1.0001,-1.0001)
        T(-1.0001,-1.0001,0.1)
        T(-1.0001,-1.0001,-0.1)
