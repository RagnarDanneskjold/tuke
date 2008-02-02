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

from Tuke.geo import Geo,Translate,Polygon
from Tuke.pcb.footprint import Pin

class TwoHole:
    """Defines a basic two hole footprint"""

    def __init__(self,id,dist,dia,thickness,clearance,mask):
        """Create a basic two hole part. 

        id 
        dist = distance between the two holes
        
        dia
        thickness
        clearance
        mask
        """

        self.id = id

        self.dist = dist
        self.dia = dia
        self.thickness = thickness
        self.clearance = clearance
        self.mask = mask

        pass

    def geo(self):
        """Generate geometry"""

        g = Geo(id=self.id) 

        a = Pin('1',self.dia,self.thickness,self.clearance,self.mask,square = True)
        b = Pin('2',self.dia,self.thickness,self.clearance,self.mask,square = False)

        a = a.geo()
        b = Translate(b.geo(),(0,self.dist))

        g.add(a)
        g.add(b)

        return g
