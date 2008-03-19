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

from Tuke import ReprableByArgsElement,SingleElement,Id

from Tuke.geometry import Layer

class Geometry(ReprableByArgsElement,SingleElement):
    """Base geometry class.

    Geometry elements define layout data such as polygons, lines and holes. All
    geometry elements have a layer attribute defining what layer(s) they belong
    too. That a object isinstance Geometry does not define how to retrieve the
    actual geometry data. That is type dependent and requires special casing by
    the renderer.

    See the Polygon and Hole classes for more info.
    """

    __defaults__ = {'layer':'*'}

    def _init(self):
        self.layer = Layer(self.layer)
