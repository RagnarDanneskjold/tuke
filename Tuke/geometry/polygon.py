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

class Polygon(SingleElement,shapely.geometry.Polygon):
    full_class_name = 'Tuke.geometry.Polygon'

    saved_state = SingleElement.saved_state + ('layer',)

    def extra_saved_state(self):
        ext = tuple(self.exterior.coords)
        int = ()
        return (('exterior-coords',ext),
                ('interior-coords',int))

    def __init__(*args,**kwargs):
        self = args[0]

        if not kwargs.has_key('id'):
            kwargs['id'] = Id()

        SingleElement.__init__(self,id=kwargs['id'])

        shapely.geometry.Polygon.__init__(*args)


        if not kwargs.has_key('layer'):
            raise Exception('Missing layer value') 

        self.layer = kwargs['layer']

    def render(self):
        return [(self.id,self.layer,self)]
