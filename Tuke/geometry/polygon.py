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

from Tuke.geometry import Geometry,Transformation 

class Polygon(Geometry):
    """A polygon"""
    
    def __init__(self,*args,**kwargs):
        """Polygon(external-coords,[internal-coords],layer='',id='')

        external_coords - ((x,y),(x,y),...)
        internal_coords - (
                           ((x,y),(x,y),...)
                           ((x,y),(x,y),...))
        """

        Geometry.__init__(self,
                layer=kwargs.setdefault('layer',''),
                id=kwargs.setdefault('id',''))

        assert(0 < len(args) < 3)

        self.external_coords = args[0]
        if len(args) == 2:
            self.internal_coords = args[1]
        else:
            self.internal_coords = ()

    def render(self):
        return (self.external_coords,self.internal_coords)
