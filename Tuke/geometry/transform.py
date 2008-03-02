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

"""Geometry transformations.

Geometry transformations are implemented by decorating every object method that
returns geometry with an appropriate type of transformation decoration.
Secondly to transform an object, use an appropriate transformation function.

Behind the scenes objects have a 'transform' attribute automatically added
and updated as needed. The decorators then apply transformations to the
geometry data before returning it.
"""

from Tuke import repr_helper
from Tuke import Element,Id

from Tuke.geometry import V

from Tuke.geometry.matrix_subclassing import OddShapeError,odd_shape_handler

from numpy import matrix,identity
from numpy.matlib import ones

from math import sin,cos

class Transformation(matrix):
    """Holder for geometry transformations.
    
    After applying a geometry transformation to a class instance a
    Transformation instance with the name 'transform' will be inserted into
    the objects dict.

    The actual transformation information is stored as a single homogeneous
    coordinate system matrix.
    """

    def __new__(cls,*args):
        """Create new geometry transformation"""

        if not args:
            args = (identity(3),)

        return super(Transformation,cls).__new__(cls,*args)
        

    def __call__(self,v):
        """Apply the Transformation to v

        v may be a bare V, or tuple/list of Vs, or any other combo.
        """

        try:
            if isinstance(v,(V,str)):
                raise TypeError

            r = []
            for n in v:
               r.append(self(n))
            return type(v)(r)
        except TypeError:
            try:
                assert isinstance(v,V)
                assert v.shape == (1,2)

                # Convert v to homogenous coordinates.
                v2 = ones(3)
                v2[0,0:2] = v

                v2 = self * v2.T

                return V(v2[0],v2[1])
            except:
                raise
                # This bit is really clever... You'd think that the resulting
                # error message would be for the inner most tuple right? But it
                # doesn't work that way, as the TypeError propegates to the
                # next outer call, and the next, and the next, each time
                # running into the following raise, until finally it gets
                # re-raised no more, this time with the full error message!
                #
                # That said, this occured completely by accident, and I only
                # noticed it had the correct behavior during testing.
                raise TypeError, 'Invalid geometry: %s' % repr(v)

    def __add__(self,other):
        """Apply the effects of other to self and return a transformation
        encompassing both."""

        r = Transformation()

        r.v = (self.v[0] + other.v[0],self.v[1] + other.v[1])

        return r

    @odd_shape_handler
    @repr_helper
    def __repr__(self):
        if self.shape != (3,3):
            raise OddShapeError

        rows = []
        for y in xrange(3):
            cols = []
            for x in xrange(3):
                cols.append(self[y,x])
            rows.append(tuple(cols))

        return ((tuple(rows),),{})

def element_transform_helper(fn):
    """Decorator for Element.transform modifying functions.
    
    Allows the function to be written in this form:

    f(*args,*kwargs) -> Transformation

    Creation of the 'transform' attribute and applying the transformation is
    handled automaticly.
    """
    def f(self,*args,**kwargs):
        if not hasattr(self,'transform'):
            self.transform = Transformation()

        self.transform = self.transform * fn(self.transform,*args,**kwargs)
    return f


def Translation(v):
    """Return a Transformation that translates by vertex v"""

    return \
        Transformation(((1.0,0.0,v[0,0]),
                        (0.0,1.0,v[0,1]),
                        (0.0,0.0,1.0)))

@element_transform_helper
def translate(e,v):
    return Translation(v)


def Rotation(a):
    """Return a Transformation that rotates by angle a"""
    return \
        Transformation((( cos(a),sin(a),0.0),
                        (-sin(a),cos(a),0.0),
                        (    0.0,   0.0,1.0)))

@element_transform_helper
def rotate(e,a):
    return Rotation(a)


def RotationAroundCenter(a,v):
    """Return a Transformation that rotates by angle a about v"""
    return Translation(v) * Rotation(a) * Translation(-v) 

@element_transform_helper
def rotate_around_center(e,a,v):
    return RotationAroundCenter(a,v)


def Scale(s):
    """Return a Transformation that scales by vector s"""
    return \
        Transformation(((s[0,0],   0.0,0.0),
                        (   0.0,s[0,1],0.0),
                        (   0.0,   0.0,1.0)))

@element_transform_helper
def scale(e,s):
    return Scale(s)
