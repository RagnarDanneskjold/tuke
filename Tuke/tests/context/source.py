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
from Tuke.context.source import Source

import sys
import gc

class SourceTest(TestCase):
    def test_Source_shadow(self):
        """Source.__dict_shadow__"""
        from Tuke.context.source import Source
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        s = Source()
        s.spam = 'spam'
        T(s.spam,'spam')

        s.__dict_shadow__['spam'] = 'ham'
        T(s.spam,'ham')
        s.spam = 'eggs'
        T(s.spam,'ham')
        T(s.__dict__['spam'],'eggs')

        # Deleting the attr shouldn't effect the shadow
        del s.spam
        T(s.spam,'ham')
        T(s.__dict__,{})

    def test_Source_notify(self):
        """Source notify"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        a = Source() 

        # Records the value of the attr when called 
        class cb:
            def __init__(self,source,attr):
                self.source = source
                self.attr = attr
                self.missing = object()

            def __call__(self,*args,**kwargs):
                T(args,())
                T(kwargs,{})

                try:
                    self.v = getattr(self.source,self.attr)
                except AttributeError:
                    self.v = self.missing
        
        # Setting a callback before the attr is created is perfectly valid.
        c = cb(a,'spam') 
        a._source_notify('spam',c)

        a.spam = 479606400
        T(c.v,479606400)

        # Callbacks are a one shot affair
        a.spam = object()
        T(c.v,479606400)

        # Callbacks are called on deletion as well
        a._source_notify('spam',c)
        del a.spam
        T(c.v is c.missing)

        # Make sure callbacks can set further callbacks
        class cb:
            def __init__(self,source,attr):
                self.source = source
                self.attr = attr
                self.v = []
            def __call__(self):
                self.source._source_notify(self.attr,self)
                self.v.append(getattr(self.source,self.attr))
        c = cb(a,'ham')
        crefs = sys.getrefcount(c)
        arefs = sys.getrefcount(a)
        a._source_notify('ham',c)
        for i in range(1000):
            a.ham = i
        T(sys.getrefcount(c),crefs)
        T(sys.getrefcount(a),arefs)
        T(c.v,list(range(1000)))

    def test_Source__shadowless__(self):
        """Source.__shadowless__"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        a = Source()
        a.__dict_shadow__['spam'] = 'ham'

        self.assertRaises(AttributeError,lambda:getattr(a.__shadowless__,'spam'))
        a.spam = 'can'
        T(a.__shadowless__.spam,'can')

        T(a.__shadowless__.__dict_shadow__.items(),[])

        # Should be completely read-only
        def f():
            a.__shadowless__.spam = 10
        self.assertRaises(TypeError,f)
        def f():
            del a.__shadowless__.spam
        self.assertRaises(TypeError,f)
        def f():
            a.__shadowless__.__dict_shadow__['foo'] = 'bar'
        self.assertRaises(TypeError,f)
        def f():
            a.__shadowless__._source_notify('foo',lambda:None)
        self.assertRaises(TypeError,f)

    def test_Source_notify_unwraps(self):
        """Source.notify unwraps callables before storing them"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        a = Element(id=Id('a'))

        called = False
        class f:
            def __init__(self):
                self.called = False
            def __call__(self):
                self.called = True
        f = f()
        a._source_notify('foo',f)
        a.foo = 10
        T(f.called)
