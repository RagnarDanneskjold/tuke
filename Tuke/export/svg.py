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

from Tuke.geometry import Polygon
from Tuke.units import MM
from Tuke.export.SVGdraw import drawing,svg,polyline,group

import shapely.geometry

def to_svg(elem):
    """Exports an element to svg"""


    # setup svg
    d = drawing()
    s = svg()

    # the viewbox sets the units to mm
    s.attributes['viewBox'] = '0mm 0mm 1000mm 1000mm'

    # Add the inkscape namespace so layers can work.
    s.namespace['xmlns:inkscape'] = 'http://www.inkscape.org/namespaces/inkscape'

    layer_groups = {}
    for i,l,g in elem.render():
        if not isinstance(g,shapely.geometry.Polygon):
            continue

        # convert coords to mm
        coords = [(x / MM,y / MM) for (x,y) in g.exterior.coords]

        pl = polyline(coords,fill='red')

        # hack to save some info
        pl.attributes['tuke-layer'] = l
        pl.attributes['tuke-id'] = i

        # Create inkscape layers for each element layer.
        g = None
        try:
            g = layer_groups[l]
        except KeyError:
            g = group(l)
            g.attributes['inkscape:groupmode'] = 'layer'
            g.attributes['inkscape:label'] = l
            layer_groups[l] = g

        g.addElement(pl)

    for g in layer_groups.values():
        s.addElement(g)

    d.setSVG(s)
    return d.toXml()
