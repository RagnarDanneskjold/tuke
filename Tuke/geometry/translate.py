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

import shapely.geometry

class Translate(Element):

    def __init__(self,g,v):
        """Translate geometry."""
        Element.__init__(self,id=Id())

        assert(isinstance(g,Element))
        assert(len(v) == 2)

        self.__g = g
        self.v = v

    def render(self):
        geo = self.__g.render()

        gnew = []
        for i,l,s in geo:
            # some shape-specific knowledge
            coords = []
            if isinstance(s,shapely.geometry.Polygon):
                for x,y in s.exterior.coords:
                    coords += [(x + self.v[0],y + self.v[1])]

                # make a new polygon
                s = shapely.geometry.Polygon(coords)

            gnew += [(i,l,s)]

        return gnew

    def save(self,doc):
        # Special case, we need to save children, but the normal "save-subs"
        # mechanism won't work because we've hidden stuff via getattr, so call
        # _save with a generated subs list.
        return self._save(doc,(self.__g,))

    def __getstate__(self):
        # More special case, we have a hidden __g attribute that shouldn't be
        # saved.
        return {'v':self.v}

    def __getattr__(self,name):
        return getattr(self.__g,name)
