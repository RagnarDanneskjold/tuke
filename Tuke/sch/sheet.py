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

from Tuke.sch import Component,Id

class Sheet(Component):
    """Defines a schematic sheet.
    
    A sheet is a collection of components representing a schematic meant to be
    encapsulated into one unit. 

    A sheet has two renderings, internal and external. The internal rendering
    shows the components the sheet is made up of. The external rendering
    presents the sheet as a box with named ports.

    A sheet is a component as well, and therefore may have pins that can be connected.
    """

    def __init__(self,id=Id()):
        """Create a sheet.

        id - Id name
        """

        Component.__init__(self,id=id)
