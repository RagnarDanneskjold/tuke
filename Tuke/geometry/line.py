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

from Tuke import SingleElement,Id
import shapely.geometry

class Line(SingleElement):
    """A line with a specified thickness."""

    def __init__(self,a,b,thickness,layer=None,id=Id()):
        SingleElement.__init__(self,id=id)

        if not layer:
            raise Exception('Missing layer value')
        if not thickness > 0:
            raise Exception('Thickness must be greater than zero')

        self.a = a
        self.b = b
        self.thickness = thickness
        self.layer = layer

    def render(self):
        # 

        # create a very thin polygon first
        p = shapely.geometry.Polygon(( \
            (self.a[0],self.a[1]),
            (self.b[0],self.b[1])))

        # and expand it with buffer
        p = p.buffer(self.thickness)

        return [(self.id,self.layer,p)]

class ThinLine(Line):
    """A line who's thickness is a multiple of the minimum resolution on the output device.""" 
