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

    # Black magic time... Basic repr is pretty easy. What's not so easy is
    # handling the V[] case, which creates a V, but with a weird shape, that
    # really should be treated, and repr-ed, as a matrix. So we leave the
    # __repr__ code as is, and insert a test to make sure the shape makes
    # sense. If it doesn't, throw an exception. The magic, is that this
    # exception gets caught by a decorator that calls the underlying
    # matrix.__repr__ method instead.
    class _odd_shape_error:
        pass

    def _odd_shape_handler(fn):
        def f(self):
            try:
                return fn(self)
            except self._odd_shape_error:
                return super(V,self.__class__).__repr__(self)
        return f

    @_odd_shape_handler
    @repr_helper
    def __repr__(self):
        if self.shape != (1,2):
            raise self._odd_shape_error

        x = int(self[0:,0])
        y = int(self[0:,1])
        return (((x,y)),{})

