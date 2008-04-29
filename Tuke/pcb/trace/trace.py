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

from Tuke import Id
from Tuke.pcb.trace import BaseTrace
from Tuke.geometry import Line,centerof

class Trace(BaseTrace):
    """Basic trace.

    Basic trace type. Creates straight lines between points of a given width.

    """

    valid_endpoint_types=()

    __defaults__ = dict(layer='pcb.top.copper')
    __required__ = ('thickness',)

    def _init(self):
        self.connects.add(Id('copper'))

    def iterlayout(self,layer_mask):
        if self.layer in layer_mask:
            if not self.a or not self.b:
                raise NotImplementedError # FIXME:

            try:
                yield self.copper
            except AttributeError:
                self.add(Line(a=centerof(self.a()),
                              b=centerof(self.b()),
                              thickness=self.thickness,
                              layer=self.layer,
                              id=Id('copper')))
                yield self.copper
