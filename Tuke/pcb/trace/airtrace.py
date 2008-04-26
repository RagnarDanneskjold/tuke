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

from Tuke.pcb.trace import BaseTrace
from Tuke.pcb import Pin

class AirTrace(BaseTrace):
    """Air wire trace.

    Air traces can only be connected to Pins. They can't be connected to
    vias, because a via can be plugged, have a solder mask over it etc.

    """

    valid_endpoint_types=(Pin,)

    __defaults__ = dict(layer='pcb.top.airtrace')

    def render(self):
        raise NotImplementedError 

