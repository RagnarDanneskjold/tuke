# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
# (c) 2008 Peter Todd <pete@petertodd.org>
#
# This program is made available under the GNU GPL version 3.0 or
# greater. See the accompanying file COPYING for details.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.

from unittest import TestCase

from Tuke import Element,Id
from Tuke.pcb import Pin,Pad
from Tuke.pcb.trace import BaseTrace

class PcbTraceBaseTraceTest(TestCase):
    """Perform tests of the pcb.footprint.Pin class"""

    def testBaseTrace(self):
        """Basic tests of BaseTrace"""

        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))


        a = Element(id=Id('a'))
        b = Element(id=Id('b'))
        a.add(b)
        b.add(Pin(dia=1,
                  thickness=1,
                  clearance=1,
                  mask=1,
                  id=Id('foo')))
        b.add(Pad(a=(0,0),
                  b=(1,1),
                  thickness=0.5,
                  clearance=0.2,
                  mask=0.6,
                  id=Id('bar')))

        class basetrace(BaseTrace):
            valid_endpoint_types = (Pin,Pad)
        a.add(basetrace(id='t'))
        a.t.set_endpoints(a.b.foo,a.b.bar)

        T(a.t.a().id,Id('a/b/foo'))
        T(a.t.b().id,Id('a/b/bar'))

        T(a.b.foo in a.t.connects)
        T(a.b.bar in a.t.connects)
        T(a.b.foo.connects.to(a.t))
        T(a.b.bar.connects.to(a.t))
