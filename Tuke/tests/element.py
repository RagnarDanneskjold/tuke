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

import sys
import weakref

import common

from unittest import TestCase
import Tuke
import Tuke.context
from Tuke.context.wrapper import unwrap
from Tuke import Element,ElementRef,Id,rndId

from Tuke.geometry import Geometry,V,Transformation,Translation,translate,centerof

class ElementTest(TestCase):
    """Perform tests of the element module"""

    def testElementIdChecks(self):
        """Element id validity checks"""

        self.assertRaises(ValueError,lambda:Element(id='foo/bar'))

    def testElement_notify(self):
        """Element.notify()"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        a = Element(id=Id('a'))

        class cb:
            def __init__(self):
                self.count = 0
            def __call__(self):
                self.count += 1

        self.assertRaises(ValueError,
                          lambda:a.topology_notify(Id('a'),lambda:None))
        self.assertRaises(ValueError,
                          lambda:a.topology_notify(Id('z/y'),lambda:None))
        self.assertRaises(TypeError,
                          lambda:a.topology_notify(Id('.'),None))

        # Test callback adding and deletion
        cb1 = cb()
        a.topology_notify(Id('a/b'),cb1)
        T(unwrap(a).__dict_callbacks__['b'],set((weakref.ref(cb1),)))
        cb2 = cb()
        a.topology_notify(Id('a/b'),cb2)
        T(unwrap(a).__dict_callbacks__['b'],
                set((weakref.ref(cb1),
                     weakref.ref(cb2))))

        del cb1
        T(unwrap(a).__dict_callbacks__['b'],set((weakref.ref(cb2),)))
        del cb2
        T(not unwrap(a).__dict_callbacks__.has_key('b')
          or unwrap(a).__dict_callbacks__['b'] == set())

        # Test that callbacks are actually called

        # Called for adding an object
        cb1 = cb()
        a.topology_notify(Id('a/b'),cb1)
        cb2 = cb()
        a.topology_notify(Id('a/b'),cb2)

        b = Element(id=Id('b'))
        cbp = cb()
        b.topology_notify(Id('.'),cbp)

        a.add(b)

        T(cb1.count,1)
        T(cb2.count,1)
        T(cbp.count,1)
        T(not unwrap(a).__dict_callbacks__.has_key('b'))
        T(not unwrap(b).__dict_callbacks__.has_key('parent'))

        # Test for removing an object, just a check that there is no .remove
        # for now.
        T(not hasattr(a,'remove'))

    def testElementCommonParent(self):
        """Element._common_parent and related functions"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        a = Element(id=Id('a'))
        b = Element(id=Id('b'))

        T(a.have_common_parent(a))
        T(b.have_common_parent(b))

        T(not a.have_common_parent(b))
        T(not b.have_common_parent(a))

        a.add(b)
        T(a.have_common_parent(b))
        T(b.have_common_parent(a))

        a.add(Element(id=Id('z')))
        a.b.add(Element(id=Id('c')))

        T(a.z.have_common_parent(a.b.c))
        T(not Element().have_common_parent(a.b.c))

    def testElementAddReturnsWrapped(self):
        """Element.add(obj) returns wrapped obj"""

        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        a = Element(id='a')

        r = a.add(Element(id='b'))
        T(a.b is r)

        r = a.b.add(Element(id='c'))
        T(a.b.c is r)

    def testElementAddCollisions(self):
        """Element.add() attr collisions"""

        def T(got,expected = True):
            self.assert_(expected == got,'got: %s expected: %s' % (got,expected))

        # Collide with an element 
        a = Element(id='a')
        b1 = a.add(Element(id='b'))
        self.assertRaises(Element.IdCollisionError,lambda:a.add(Element(id='b')))

        # collide with attr
        a = Element(id='a')
        a.b = 10
        b1 = a.add(Element(id='b'))
        T(a.b,10)
        T(a['b'],b1)

    def testElementAddObjChecks(self):
        """Element.add(obj) checks that obj is valid"""

        def T(ex,obj):
            self.assertRaises(ex,lambda:Element().add(obj))

        # Basic wrongness
        T(TypeError,None)
        T(TypeError,'asdf')
        T(TypeError,2)

        # Check for wrapped subelements, IE, added element already has a
        # parent.
        T(ValueError,Element().add(Element()))

    def testElementInteration(self):
        """Element interation"""

        def T(elem,id_set):
            ids = set() 
            for e in elem:
                if isinstance(e,Element):
                    ids.add(e.id)
            id_set = set([Id(i) for i in id_set])
            self.assert_(ids == id_set,'got: %s expected: %s' % (ids,id_set))

        a = Element(id='a')
        T(a,set())

        for i in range(1,4):
            a.add(Element(id='_' + str(i)))

        T(a,set(('a/_1','a/_2','a/_3')))

    def testElement__getitem__(self):
        """Element[] lookups"""
        def T(elem,key,expected_id):
            got = elem[key]
            expected_id = Id(expected_id)
            self.assert_(got.id == expected_id,'got: %s expected: %s' % (got.id,expected_id))

        def R(elem,key,partial_stack):
            # partial_stack is not currently used, but
            err = None
            self.assertRaises(KeyError,lambda:elem[key])

        a = Element(id='a')
        T(a,'','a')
        R(a,'foo',[])
        R(a,Id('foo'),[])
        R(a,'..',[a])
        R(a,'../b',[a])
        R(a,'../..',[a])

        b = a.add(Element(id='b'))
        T(a,'b','a/b')
        with b as b2:
            R(a,'b/b',[a,b2])
            R(b2,'../c',[b2,a])

        c = a.add(Element(id='c'))
        T(a,'c','a/c')

        d = a.b.add(Element(id='d'))
        T(a,'b','a/b')
        T(a,'b/d','a/b/d')

        T(b,'..',a['.'].id)
        T(b,'../b',b.id)
        T(b,'../b/d',d.id)

        e = Element(id='e')
        e2 = a.add(e)
        a['e'].foo = 'foo'
        self.assert_(e2.foo is e.foo)
        self.assert_(a.e.foo is e.foo)
        self.assert_(a['e'].foo is e.foo)

    def testElementIterlayout(self):
        """Element.iterlayout()"""

        def T(got,expected = True):
            self.assert_(expected == got,'expected: %s  got: %s' % (expected,got))

        e = Element(id='base')

        e.add(Element(id='chip'))
        e.chip.add(Element(id='pad'))
        e.chip.add(Geometry(layer='sch.lines',id='sym'))
        e.chip.pad.add(Geometry(layer='top.copper',id='pad'))

        # Check returned objects and Id auto-mangling
        T(set([elem.id for elem in e.iterlayout()]),
          set((Id('base/chip/pad/pad'), Id('base/chip/sym'))))

        # Check that transforms are working
        translate(e.chip,V(1,1))

        [T(repr(elem.transform), repr(Translation(V(1.0, 1.0))))
            for elem in e.iterlayout()]

        translate(e.chip.pad,V(2,3))

        r = {Id('base/chip/sym'):Translation(V(1.0, 1.0)),
             Id('base/chip/pad/pad'):Translation(V(3.0, 4.0))}

        for elem in e.iterlayout():
            T(repr(r[elem.id]), repr(elem.transform))

        # Check layer filtering works
        T(set([elem.id for elem in e.iterlayout(layer_mask='top.*')]),
          set((Id('base/chip/pad/pad'),)))
        T(set([elem.id for elem in e.iterlayout(layer_mask='sch.*')]),
          set((Id('base/chip/sym'),)))

    def testElement_with(self):
        """with Element()"""

        a = Element(id='a')
        b = Element(id='b')
        a.add(b)

        with a.b as b2:
            self.assert_(b is b2)

    def testElementIdAttr(self):
        """Auto-magical attribute lookup from sub-element Id's"""

        a = Element(id=Id('a'))
        translate(a,V(1,1))

        foo = Element(id=Id('foo'))
        translate(foo,V(2,1))
        bar = Element(id=Id('bar'))
        translate(bar,V(1,2))

        a.add(foo)
        a.add(bar)

        self.assert_(a.foo.id == Id('a/foo'))
        self.assert_(repr(centerof(a.foo)) == repr(V(3,2)))
        self.assert_(a.bar.id == Id('a/bar'))
        self.assert_(repr(centerof(a.bar)) == repr(V(2,3)))
        self.assertRaises(AttributeError,lambda: a.foobar)

        foo.foo = 'foo'
        self.assert_(a.foo.foo is foo.foo)
        a.foo.bar = 'bar'
        self.assert_(a.foo.bar is foo.bar)

    def testElementVersionChecking(self):
        """Element __version__ checking"""

        return

        #FIXME: needs a lot of reworking

        class elem(Element):
            __version__ = (1,2)

        def T(ver):
            a = elem()
            a.__version__ = ver
            self.assert_(elem.from_older_version(a) == a)

        def F(ver):
            a = elem()
            a.__version__ = ver
            self.assertRaises(elem.VersionError,lambda: elem.from_older_version(a))

        def R(ver):
            a = Element()
            a.__version__ = ver
            self.assertRaises(ValueError,lambda: srElement.from_older_version(a))

        T((1,2))
        T((1,1))
        T((1,1,45))
        T((1,1,45,'sdf'))

        F((1,3))
        F((0,2))
        F((2,2))

        R(None)
        R('wr')
        R((0,))
        R((0,'sdf'))
        R([0,'sdf'])

    def testElement__init_does_not_mangle_properties(self):
        """Element._init() system does not mangle properties"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        # If the Element._init() stuff is implemented to use __dict__ directly,
        # rather than setattr, properties get mangled at initialization.

        class SkinnerBox(Element):
            __defaults__ = dict(open=False,prop_set=0,prop_got=0)
            def get_open(self):
                self.prop_got += 1
                return self._open
            def set_open(self,v):
                self.prop_set += 1
                self._open = v
            open = property(get_open,set_open)

        box = SkinnerBox()
        T(box.open,False)
        T(box.prop_got,1)
        T(box.prop_set,1)

        box.open = True
        T(box.prop_got,1)
        T(box.prop_set,2)

        T(box.open,True)
        T(box.prop_got,2)
        T(box.prop_set,2)

        # A previous version of repr_kwargs had the same incorrect usage of
        # __dict__, catch that.
        T(repr(box).find('open') > 0)

    def testElementSerialize(self):
        """Element.serialize()"""

        a = Element(id='')

        from Tuke.geometry import Circle,Hole,Line
        from Tuke.pcb import Pin,Pad

#        a.add(Element(Id('asdf')))
#        a.add(Circle(1,'foo',id=rndId()))
#        a.add(Line((0.1,-0.1),(2,3),0.05,'foo',id=rndId()))
#        a.add(Hole(3,id=rndId()))
#        a.add(Pin(1,0.1,0.1,1,id=rndId()))
#        a.add(Pin(1,0.1,0.1,1,square=True,id=rndId()))
#        a.add(Pad((0,0),(0,1),0.5,0.1,0.6,id=rndId()))
#        a.subs[0].add(Element())

        from Tuke.geda import Footprint
        common.load_dataset('geda_footprints')
        f1 = Footprint(file=common.tmpd + '/plcc4-rgb-led')
        f2 = Footprint(file=common.tmpd + '/supercap_20mm')
      
        print f1.serialize(sys.stdout,full=True)
        print f2.serialize(sys.stdout,full=True)
        # FIXME: more needed here...
