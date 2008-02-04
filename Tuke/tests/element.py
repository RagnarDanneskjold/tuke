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
from Tuke import Element,Id,rndId

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

    def testElementSave(self):
        """Element.save()"""

        doc = Document()

        a = Element()

        from Tuke.geometry import Circle,Hole,Line
        from Tuke.pcb.footprint import Pin,Pad

        a.add(Element(Id('asdf')))
        a.add(Circle(1,'foo',id=rndId()))
        a.add(Line((0.1,-0.1),(2,3),0.05,'foo',id=rndId()))
        a.add(Hole(3,id=rndId()))
        a.add(Pin(1,0.1,0.1,1,id=rndId()))
        a.add(Pin(1,0.1,0.1,1,square=True,id=rndId()))
        a.add(Pad((0,0),(1,1),0.5,0.1,0.6,id=rndId()))
        a.subs[0].add(Element())

        from Tuke.geda import Footprint
        common.load_dataset('geda_footprints')
        f1 = Footprint(common.tmpd + '/plcc4-rgb-led',Id('plcc4'))
        f2 = Footprint(common.tmpd + '/supercap_20mm',Id('supercap'))
        a.add(f1)
        a.add(f2)

        print a.save(doc).toprettyxml(indent="  ")
