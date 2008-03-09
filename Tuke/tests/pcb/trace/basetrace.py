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

from Tuke import Element
from Tuke.pcb import Pin,Pad
from Tuke.pcb.trace import BaseTrace

class PcbTraceBaseTraceTest(TestCase):
    """Perform tests of the pcb.footprint.Pin class"""

    def testBaseTrace(self):
        """Basic tests"""

        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        a = Element('a')
        b = Element('b')
        a.add(Element('b'))
        b.add(Pin(1,1,1,1,id='foo'))
        b.add(Pad((0,0),(1,1),0.5,0.2,0.6,id='bar'))

        a.add(BaseTrace(b.foo,b.bar,id='t',valid_endpoint_types=(Pin,Pad)))
    
        T(a.t.a.id,'b/foo')
        T(a.t.b.id,'b/bar')


        def R(a,b,bad_endpoints,valid_endpoint_types):
            try:
                BaseTrace(a,b,valid_endpoint_types=valid_endpoint_types)
            except BaseTrace.InvalidEndpointTypeError,ex:
                T(ex.bad_endpoints,bad_endpoints)
                return
            T(bad_endpoints,'no exception raised')
        
        R(b.foo,b.bar,set((b.foo,b.bar)),valid_endpoint_types=())
        R(b.foo,b.bar,set((b.foo,)),valid_endpoint_types=(Pad,))
        R(b.foo,b.bar,set((b.bar,)),valid_endpoint_types=(Pin,))
        R(None,None,set((None,None)),valid_endpoint_types=(Pin,Pad))
