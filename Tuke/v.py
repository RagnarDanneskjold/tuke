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

from numpy import matrix

from Tuke import repr_helper

class V(matrix):
    """2d vector
    
    Based on a numpy matrix.
    """

    def __new__(cls,x,y):
        """Create a new vector with x,y as the coordinates."""

        return super(V,cls).__new__(cls,(float(x),float(y)))

    @repr_helper
    def __repr__(self):
        assert self.shape == (1,2)

        x = int(self[0:,0])
        y = int(self[0:,1])
        return (((x,y)),{})

