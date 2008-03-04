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
from Tuke import load_Element,Element,Id,rndId

from Tuke.geometry import Geometry,V,Transformation,Translation,translate,centerof

from xml.dom.minidom import Document

class ElementTest(TestCase):
    """Perform tests of the element module"""

    def testElementIdChecks(self):
        """Element id validity checks"""

        self.assertRaises(ValueError,lambda:Element('foo/bar'))

    def testElementInterator(self):
        """Element interation"""

        a = Element()

        j = set((Element(),Element(),Element()))

        for i in j:
            a.add(i)

        self.assert_(set(iter(a)) == j)

    def testElementIterlayout(self):
        """Element.iterlayout()"""

        def T(x):
            self.assert_(x)

        e = Element(id='base')

        e.add(Element(id = 'chip'))
        e.chip.add(Element(id = 'pad'))
        e.chip.add(Geometry(layer = 'sch.lines',id = 'sym'))
        e.chip.pad.add(Geometry(layer = 'top.copper',id = 'pad'))

        # Check returned objects and Id auto-mangling
        T(set([elem.id for elem in e.iterlayout()]) ==
          set((Id('base/chip/pad/pad'), Id('base/chip/sym'))))

        # Check that transforms are working
        translate(e.chip,V(1,1))

        print [repr(elem.transform) for elem in e.iterlayout()]
        [T(repr(elem.transform) == repr(Translation(V(1.0, 1.0))))
            for elem in e.iterlayout()]

        translate(e.chip.pad,V(2,3))

        r = {Id('base/chip/sym'):Translation(V(1.0, 1.0)),
             Id('base/chip/pad/pad'):Translation(V(3.0, 4.0))}

        for elem in e.iterlayout():
            T(repr(r[elem.id]) == repr(elem.transform))

        # Check layer filtering works
        T(set([elem.id for elem in e.iterlayout(layer_mask='top.*')]) ==
          set((Id('base/chip/pad/pad'),)))
        T(set([elem.id for elem in e.iterlayout(layer_mask='sch.*')]) ==
          set((Id('base/chip/sym'),)))

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

    def testElementSave(self):
        """Element.save()"""

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
        f1 = Footprint(common.tmpd + '/plcc4-rgb-led',Id('plcc4'))
        f2 = Footprint(common.tmpd + '/supercap_20mm',Id('supercap'))
        a.add(f1)
        a.add(f2)

        dom = a.save(doc)

        print a.save(doc).toprettyxml(indent="  ")

        doc = Document()
        print load_Element(dom).save(doc).toprettyxml(indent="  ")
        
