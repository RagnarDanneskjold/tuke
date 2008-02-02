# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
# ### BOILERPLATE ###
# Tuke - Electrical Design Automation toolset
# Copyright (C) 2008 Peter Todd <pete@petertodd.org>
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ### BOILERPLATE ###

from Tuke import Element,Id
from Tuke.geometry import Translate
from Tuke.pcb.footprint import Pin,Pad

import re

class Footprint(Element):
    """Wrapper for gEDA/PCB footprints"""


    def __init__(self,file,id=Id()):
        Element.__init__(self,id=id)

        f = open(file,"r")

        translate = None

        for l in f:
            l = l.strip()

            tag = re.findall(r'^(ElementArc|ElementLine|Element|Pin|Pad)',l)

            if len(tag):

                v = re.findall(r'\[.*\]',l)

                # FIXME: add detection for mil units in () brackets
                mul = 1

                v = v[0][1:-1].split(' ')

                if tag[0] == 'Element':
                    (element_flags,description,pcb_name,value,mark_x,mark_y,text_x,text_y,text_direction,text_scale,text_flags) = v

                    mark_x = int(mark_x)
                    mark_y = int(mark_y)
                    text_x = int(text_x)
                    text_y = int(text_y)

                    mark_x *= mul
                    mark_y *= mul
                    text_x *= mul
                    text_y *= mul

                    # Setup translation function
                    translate = lambda x: Translate(x,(mark_x,mark_y))

                elif tag[0] == 'Pin':
                    (x,y,thickness,clearance,mask,dia,name,pin_number,flags) = v
                    x = int(x) * mul
                    y = int(y) * mul
                    thickness = int(thickness) * mul
                    clearance = int(clearance) * mul
                    mask = int(mask) * mul
                    dia = int(dia) * mul

                    pin_number = pin_number[1:-1] # remove quotes

                    p = Pin(dia,thickness,clearance,mask,id=pin_number)
                    p = Translate(p,(x,y))

                    self.add(translate(p))

                elif tag[0] == 'Pad':
                    (x1,y1,x2,y2,thickness,clearance,mask,name,pad_number,flags) = v

                    x1 = int(x1) * mul
                    y1 = int(y1) * mul
                    x2 = int(x2) * mul
                    y2 = int(y2) * mul
                    thickness = int(thickness) * mul
                    clearance = int(clearance) * mul
                    mask = int(mask)

                    pad_number = pad_number[1:-1] # remove quotes

                    p = Pad((x1,y1),(x2,y2),thickness,clearance,mask,id=pad_number)

                    self.add(translate(p))
