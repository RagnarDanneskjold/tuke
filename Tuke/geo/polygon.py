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

from geo import BaseGeo
import shapely.geometry

class Polygon(BaseGeo,shapely.geometry.Polygon):
    def __init__(*args,**kwargs):
        self = args[0]
        BaseGeo.__init__(self,id=kwargs['id'])

        shapely.geometry.Polygon.__init__(*args)


        if not kwargs.has_key('id'):
            kwargs['id'] = ''
        if not kwargs.has_key('layer'):
            raise None

        self.id = kwargs['id']
        self.layer = kwargs['layer']


    def add(self,b):
        """Polygon's can't include sub-geometry"""
        raise None
