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

from Tuke import ReprableByArgsElement

class Footprint(ReprableByArgsElement):
    """Defines a Footprint.
  
    A footprint is the holder for the geometry data comprising a pcb footprint.
    Footprints contain any number of geometry elements, from simple
    constructions such as lines to more complex constructions such as Pins and
    Pads.

    Footprints always have an id of 'footprint'
    """
    def __init__(self,kwargs,required=(),defaults={}):
        assert not kwargs.has_key('id')
        kwargs['id'] = 'footprint'
        ReprableByArgsElement.__init__(self,kwargs,required,defaults)
