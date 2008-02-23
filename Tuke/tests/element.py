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

from xml.dom.minidom import Document

class ElementTest(TestCase):
    """Perform tests of the element module"""

    def testElementInterator(self):
        """Element interation"""

        a = Element()

        j = set((Element(),Element(),Element()))

        for i in j:
            a.add(i)

        self.assert_(set(a.subs) == j)

    def testElementIterlayout(self):
        """Element.iterlayout()"""

        def T(x):
            self.assert_(x)

        from Tuke.geometry import Geometry

        e = Element(id='base')

        e.add(Element(id = 'chip'))
        e.chip.add(Element(id = 'pad'))
        e.chip.add(Geometry(layer = 'sch.lines',id = 'sym'))
        e.chip.pad.add(Geometry(layer = 'top.copper',id = 'pad'))

        # Check returned objects and Id auto-mangling
        T(set([elem.id for elem in e.iterlayout()]) ==
          set((Id('base/chip/pad/pad'), Id('base/chip/sym'))))

        # Check that transforms are working
        from Tuke.geometry import translate,Transformation
        translate(e.chip,v=(1,1))

        [T(elem.transformed == Transformation(v = (1.0, 1.0)))
            for elem in e.iterlayout()]

        translate(e.chip.pad,v=(2,3))

        r = {Id('base/chip/sym'):Transformation(v = (1.0, 1.0)),
             Id('base/chip/pad/pad'):Transformation(v = (3.0, 4.0))}

        for elem in e.iterlayout():
            T(r[elem.id] == elem.transformed)

        # Check layer filtering works
        T(set([elem.id for elem in e.iterlayout(layer_mask='top.*')]) ==
          set((Id('base/chip/pad/pad'),)))
        T(set([elem.id for elem in e.iterlayout(layer_mask='sch.*')]) ==
          set((Id('base/chip/sym'),)))

    def testElementIdAttr(self):
        """Auto-magical attribute lookup from sub-element Id's"""

        a = Element()

        foo = Element(id='foo')
        bar = Element(id='bar')

        a.add(foo)
        a.add(bar)

        self.assert_(a.foo == foo)
        self.assert_(a.bar == bar)
        self.assertRaises(AttributeError,a.__getattr__,'foobar')

    def testElementSave(self):
        """Element.save()"""

        doc = Document()

        a = Element()

        from Tuke.geometry import Circle,Hole,Line
        from Tuke.pcb.footprint import Pin,Pad

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
        
