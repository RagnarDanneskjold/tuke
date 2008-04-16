# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
# (c) 2008 Peter Todd <pete@petertodd.org>
#
# This program is made available under the GNU GPL version 3.0 or
# greater. See the accompanying file COPYING for details.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.

from __future__ import with_statement

from unittest import TestCase

from Tuke import Element,Id
import Tuke.context as context

import sys
import gc

class WrapperTest(TestCase):
    def test_wrap_with_non_element_context(self):
        """wrap() checks that context is an Element instance"""

        self.assertRaises(TypeError,lambda: context.wrap(None,None))

    def test_Wrapped_obj_context_refcounts(self):
        """Wrapped maintains correct ref counts for obj and context"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        a = Element(id=Id('a'))
        b = Element(id=Id('b'))

        # Check ref counting behavior
        ref_orig_a = sys.getrefcount(a)
        ref_orig_b = sys.getrefcount(a)
        w = context.wrap(b,a)
        T(sys.getrefcount(a) - ref_orig_a,1)
        T(sys.getrefcount(b) - ref_orig_b,1)

        del w
        T(sys.getrefcount(a) - ref_orig_a,0)
        T(sys.getrefcount(b) - ref_orig_b,0)

    def test_isinstance_Wrapped(self):
        """isinstance(Wrapped)"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        a = Element(id=Id('a'))
        b = Element(id=Id('b'))

        w = context.wrap(b,a)

        T(isinstance(w,context.Wrapped))
        T(isinstance(w,Element))

    def test_is_Wrapped(self):
        """Wrapped(foo) is Wrapped(foo)"""
        keys = context.wrapper._wrapped_cache.keys()

        # These objects aren't supposed to be wrapped.
        def T(obj):
            a = Element(id=Id('a'))
            self.assert_(context.wrap(obj,a) is obj)
        T(None)
        T(True)
        T(False)
        T(3)
        T(31415)
        T(3.14)
        T(10j)
        T(type(None))
        T(type(self))
        T('foo')
        T(u'foo')

        import tempfile
        f = tempfile.TemporaryFile()
        T(f)

        # These objects are supposed to be wrapped.
        def T(obj):
            a = Element(id=Id('a'))
            self.assert_(context.wrap(obj,a) is context.wrap(obj,a))
        T(object())
        T({})

        self.assert_(context.wrapper._wrapped_cache.keys() == keys)

    def test_circular_Wrapped_are_garbage_collected(self):
        """Wrapped objects with circular references are garbage collected"""

        keys = context.wrapper._wrapped_cache.keys()
        a = Element(id=Id('a'))

        class foo(Element):
            pass

        b = foo(id=Id('b')) 
        b.a = context.wrap(b,a)

        del a
        del b
        import gc
        gc.collect(2)
        self.assert_(context.wrapper._wrapped_cache.keys() == keys)

    def test_Wrapped_getset_attr(self):
        """(get|set)attr on Wrapped object"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        def R(ex,fn):
            self.assertRaises(ex,fn)

        a = Element(id=Id('a'))
        b = Element(id=Id('b'))

        w = context.wrap(b,a)

        R(AttributeError,lambda: w.VenezuelanBeaverCheese)
       
        n = "NorweiganJarlsburg"
        n_refc = sys.getrefcount(n)
        R(AttributeError,lambda: getattr(w,n))
        T(sys.getrefcount(n),n_refc)
       
        n = "Abuse"
        n_refc = sys.getrefcount(n)
        v = "vacuous, coffee-nosed, maloderous, pervert"
        v_refc = sys.getrefcount(n)
        setattr(w,n,"vacuous, coffee-nosed, maloderous, pervert")
        T(sys.getrefcount(n) - 1,n_refc)
        T(sys.getrefcount(v) - 1,v_refc)

        T(w.Abuse,v) 
        T(sys.getrefcount(n) - 1,n_refc)
        T(sys.getrefcount(v) - 1,v_refc)

    def test_Wrapped_hash(self):
        """hash(Wrapped)"""
        a = Element(id=Id('a'))

        class smoot:
            def __hash__(self):
                return 1930
        b = smoot()
        w = context.wrap(b,a)

        self.assert_(hash(b) == 1930)
        self.assert_(hash(w) == 1930)

    def test_Wrapped_data_in_out(self):
        """Wrapped data in/out"""

        def W(obj,expected_applied,expected_removed):
            context_element = Element(id=Id('a'))
            applied = context.wrapper._apply_remove_context(context_element,obj,1)
            self.assert_(expected_applied == applied,
                    'applied context, got: %s  expected: %s'
                     % (applied,expected_applied))
            removed = context.wrapper._apply_remove_context(context_element,obj,0)
            self.assert_(expected_removed == removed,
                    'removed context, got: %s  expected: %s'
                     % (removed,expected_removed))

        class skit(object):
            def __init__(self,id):
                self.id = Id(id)
            def __eq__(self,other):
                return self.id == other.id

        # tuples
        W((),(),())
        W((1,),(1,),(1,))
        W((Id('b'),),(Id('a/b'),),(Id('../b'),))
        W((skit('b'),),(skit('a/b'),),(skit('../b'),))

        # lists
        W([],[],[])
        W([1,],[1,],[1,])
        W([Id('b'),],[Id('a/b'),],[Id('../b'),])
        W([skit('b'),],[skit('a/b'),],[skit('../b'),])
