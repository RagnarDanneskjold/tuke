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

from Tuke.pcb.footprint import Pin,Pad
from Tuke.geo import Geo,Translate

import re

class Footprint:
    """Wrapper for gEDA/PCB footprints"""


    def __init__(self,id,file):
        
        self.id = id

        f = open(file,"r")

        self.g = Geo(id=self.id)
        for l in f:
            l = l.strip()

            tag = re.findall(r'^(ElementLine|Element|Pin|Pad)',l)

            if len(tag):

                v = re.findall(r'\[.*\]',l)

                # FIXME: add detection for mil units in () brackets
                mul = 1

                v = v[0][1:-1].split(' ')

                if tag[0] == 'Element':
                    (element_flags,description,pcb_name,value,mark_x,mark_y,text_x,text_y,text_direction,text_scale,text_flags) = v

                    mark_x *= mul
                    mark_y *= mul
                    text_x *= mul
                    text_y *= mul

                    # Setup translation
                    self.g = Translate(self.g,(mark_x,mark_y))

                elif tag[0] == 'Pin':
                    print tag
                    print v
                    pass
                elif tag[0] == 'Pad':
                    (x1,y1,x2,y2,thickness,clearance,mask,name,pad_number,flags) = v

                    x1 *= mul
                    y1 *= mul
                    x2 *= mul
                    y2 *= mul

                    p = Pad(pad_number,(x1,y1),(x2,y2),thickness,clearance,mask)

                    self.g.add(p.geo())

                    pass
