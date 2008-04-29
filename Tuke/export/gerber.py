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

from Tuke.geometry import Hole,centerof
from Tuke.units import IN,MIL

import shapely.geometry

def to_gerber(elem):
    """Exports an element to gerber RS274X
    
    Returns a dict of the different layers encountered.
    """

    layers = {}

    # key is size, value is list of vertexes
    drill_hits = {}

    for g in elem.iterlayout():
        def s(n):
            """Convert float n meters to gerber 3.5 format, (inches) leading zeros removed"""
           
            n = (n / IN) * 1e+5

            # The int() effectively removes tailing decimals and leading zeros.
            return str(int(n))

        if hasattr(g,'render'):
            (coords,ext_coords) = g.render()

            l = str(g.layer)

            # convert coords to mm
            def t(v):
                return (s(v[0,0]),s(v[0,1]))
            coords = [t(v) for v in coords]

            # Create gerber layers for each element layer.
            if not layers.has_key(l):
                layers[l] = ''

            # Comment for debugging
            layers[l] += 'G04 id: %s *\n' % str(g.id)

            # start Polygon Area Fill code
            layers[l] += 'G36*\n'

            # first vertex gets repeated to close the polygon
            layers[l] += 'X%sY%sD02\n' % (str(coords[0][1]),str(coords[0][1]))

            # rest of the vertexes are handled normally
            for (x,y) in coords:
                layers[l] += 'X%sY%sD01*\n' % (str(x),str(y))

            layers[l] += 'G37*\n'
        elif isinstance(g,Hole):
            l = None
            # dia is expressed as 0.000 in inches
            dia = str(round(g.dia / IN,3))
            try:
                l = drill_hits[dia]
            except KeyError:
                l = []
                drill_hits[dia] = l
            l.append(centerof(g))

    # add program end markers to all layers
    for l in layers.keys():
        layers[l] += 'M02*\n'

    # prepend parameter blocks to all layers
    for l in layers.keys():
        comment = 'G04 layer: %s *\n' % l
        layers[l] = comment + \
"""
%MOIN*%
%FSLAX35Y35*%
%ADD11C,0.0200*%
""" + layers[l]

    # Create drill layer
    drill = []
    drill.append('M48')
    drill.append('INCH,TZ')
    for n,dia in enumerate(sorted(drill_hits.keys())):
        drill.append('T%dC%s' % (n + 11,dia))
    drill.append('%')

    for n,dia in enumerate(sorted(drill_hits.keys())):
        drill.append('T%d' % (n + 11))
        for v in drill_hits[dia]:
            # Gerber drill file stores drill locations in to 4 decimal points
            # in inches, but with the decimal point dropped.
            #
            # 12.3456 in -> 123456
            #
            # Note that there must be exactly six digits, padding with leading
            # zeros.
            def s(x):
                return '%0.6d' % ((x / IN) * 10000)
            x = s(v[0,0])
            y = s(v[0,1])
            drill.append('X%sY%s' % (x,y))
    drill.append('M30')
    layers['drill'] = '\n'.join(drill)

    return layers 
