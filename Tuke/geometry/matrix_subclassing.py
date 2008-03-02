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

"""Utility functions for classes that subclass numpy.matrix"""

class OddShapeError(Exception):
    """Matrix is an odd shape."""
    pass

def odd_shape_handler(fn):
    """Decorator for __repr__ functions that need to handle odd shaped matrixes.

    If the matrix class is subclassed the __repr__ function is likely going to
    be written assuming a certain shape, or set of shapes. However in a number
    of circumstances this won't be true, for instance, if a slice of the matrix
    is selected. The new classes __repr__ must still be able to handle this
    though. This decorator catches OddShapeError exceptions and calls the base
    class __repr__ function instead, handling the error.
    """
    def f(self):
        try:
            return fn(self)
        except OddShapeError: 
            return super(self.__class__,self).__repr__()
    return f
