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

import os
import shutil

import common

from unittest import TestCase
import Tuke
from Tuke import Element,ElementRef,Id,rndId

from Tuke.geometry import Geometry,V,Transformation,Translation,translate,centerof

from xml.dom.minidom import Document

class ElementTest(TestCase):
    """Perform tests of the element module"""

    def testElementIdChecks(self):
        """Element id validity checks"""

        self.assertRaises(ValueError,lambda:Element('foo/bar'))

    def testElementParent(self):
        """Element.parent"""

        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        a = Element('a')
        b = Element('b')

        T(b.parent,None)
        T(b.parent_set_callback,[])
        T(b.parent_unset_callback,[])

        called = [] 
        def c(self):
            called.append(self)
        b.parent_set_callback.append(c)

        a.add(b)
        T(b.parent,a)
        T(called,[b])

    def testElementAddReturnsWrapped(self):
        """Element.add(obj) returns wrapped obj"""

        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        a = Element('a')

        r = a.add(Element('b'))
        T(a.b is r)

        r = a.b.add(Element('c'))
        T(a.b.c is r)

    def testElementAddCollisions(self):
        """Element.add() attr collisions"""

        def T(got,expected = True):
            self.assert_(expected == got,'got: %s expected: %s' % (got,expected))

        # Collide with an element 
        a = Element('a')
        b1 = a.add(Element('b'))
        self.assertRaises(Element.IdCollisionError,lambda:a.add(Element('b')))

        # collide with attr
        a = Element('a')
        a.b = 10
        b1 = a.add(Element('b'))
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

        # Check for wrapped subelements
        T(TypeError,Element().add(Element()))

    def testElementInteration(self):
        """Element interation"""

        def T(elem,id_set):
            ids = set() 
            for e in elem:
                if isinstance(e,Element):
                    ids.add(e.id)
            id_set = set([Id(i) for i in id_set])
            self.assert_(ids == id_set,'got: %s expected: %s' % (ids,id_set))

        a = Element('a')
        T(a,set())

        for i in range(1,4):
            a.add(Element('_' + str(i)))

        T(a,set(('a/_1','a/_2','a/_3')))

    def testElement_isinstance(self):
        """Element isinstance()"""

        def T(x):
            self.assert_(x)

        a = Element('a')
        T(isinstance(a,Element))
        T(not isinstance(a,ElementRef))

        a.add(Element('b'))
        T(isinstance(a.b,Element))
        T(isinstance(a.b,ElementRef))

    def testElement__getitem__(self):
        """Element[] lookups"""
        def T(elem,key,expected):
            got = elem[key]
            self.assert_(expected == got,'got: %s expected: %s' % (got,expected))

        def R(elem,key,ex):
            self.assertRaises(ex,lambda: elem[key])

        a = Element('a')
        T(a,'',a)
        R(a,'foo',KeyError)
        R(a,Id('foo'),KeyError)

        b = a.add(Element('b'))
        T(a,'b',b)
        R(a,'b/b',KeyError)

        c = a.add(Element('c'))
        T(a,'c',c)

        d = a.b.add(Element('d'))
        T(a,'b',b)
        T(a,'b/d',d)

        #T(b,'..',a)
        #T(b,'../b',b)
        #T(b,'../d',d)

        e = Element('e')
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

        e.add(Element(id = 'chip'))
        e.chip.add(Element(id = 'pad'))
        e.chip.add(Geometry({'layer':'sch.lines','id':'sym'}))
        e.chip.pad.add(Geometry({'layer':'top.copper','id':'pad'}))

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

        a = Element('a')
        b = Element('b')
        a.add(b)

        with a.b as b2:
            self.assert_(b is b2)

    def testElementIdAttr(self):
        """Auto-magical attribute lookup from sub-element Id's"""

        a = Element(id='a')
        translate(a,V(1,1))

        foo = Element(id='foo')
        translate(foo,V(2,1))
        bar = Element(id='bar')
        translate(bar,V(1,2))

        a.add(foo)
        a.add(bar)

        self.assert_(a.foo.id == 'a/foo')
        self.assert_(repr(centerof(a.foo)) == repr(V(3,2)))
        self.assert_(a.bar.id == 'a/bar')
        self.assert_(repr(centerof(a.bar)) == repr(V(2,3)))
        self.assertRaises(AttributeError,lambda: a.foobar)

        foo.foo = 'foo'
        self.assert_(a.foo.foo is foo.foo)
        a.foo.bar = 'bar'
        self.assert_(a.foo.bar is foo.bar)

    def testElementVersionChecking(self):
        """Element __version__ checking"""
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
            self.assertRaises(ValueError,lambda: Element.from_older_version(a))

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

    def testElementSerialize(self):
        """Element.serialize()"""

        doc = Document()

        a = Element()

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
      
        print f1.serialize(full=True)
        print f2.serialize(full=True)
        # FIXME: more needed here...
