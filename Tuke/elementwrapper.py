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

from Tuke import Element,non_evalable_repr_helper

# Cache of ElementWrappers, stored with (id(base),id(obj)) as keys.
#
# Possible bug... Could potentially return a value, if base and object are both
# deleted and others end up at the same address, seems unlikely though.
import weakref
ElementWrapper_cache = weakref.WeakValueDictionary()

class ElementWrapper(object):
    """Class to wrap a sub-Element's id and transform attrs.
    
    This is the magic that allows foo.bar.id to be 'foo/bar', even though
    seperately foo.id == 'foo' and bar.id == 'bar'

    """

    # Since isinstance(e,Element) must work ElementWrappers are implemented
    # using __getattribute__ Except for __class__ accesses the logic is quite
    # simple, if the name is in ElementWrapper.__dict__, return self.name,
    # otherwise, self._obj.name Therefore the following names must be declared
    # in the class context.
    _obj = None
    _base = None
    _wrapped_class = None

    def __new__(cls,base,obj):
        """Create a new ElementWrapper

        base - base element
        obj - wrapped element

        A subtle point is that for any given (id(base),id(obj)) only one
        ElementWrapper object will be created, subsequent calls will return
        the same object. This is required not just for performence reasons, but
        to maintain the following invarient:
            
        a.b.add(Element('c')) == a.b.c
        """

        cache_key = (id(base),id(obj))
        try:
            return ElementWrapper_cache[cache_key]
        except KeyError:
            self = object.__new__(cls)

            assert(isinstance(base,Element))
            assert(isinstance(obj,(Element,ElementWrapper)))
            self._base = base
            self._obj = obj 

            # Create a subclass of the wrapped objects class, so
            # isinstance(e,ElementWrapper) works.
            if isinstance(obj,ElementWrapper):
                self._wrapped_class = obj.__class__
            else:
                self._wrapped_class = \
                        type('ElementWrapper',
                             (ElementWrapper,obj.__class__),
                             {})

            ElementWrapper_cache[cache_key] = self
            return self

    def add(self,obj):
        return ElementWrapper(self._base,
                self._obj.add(obj))

    def _wrapper_get_id(self):
        return self._base.id + self._obj.id
    id = property(_wrapper_get_id)

    def _wrapper_get_transform(self):
        return self._base.transform * self._obj.transform
    def _wrapper_set_transform(self,value):
        # The code setting transform will be dealing with the transform
        # relative to the wrapper, however _obj.transform needs to be stored
        # relative to _obj. So apply the inverse of the base transformation
        # before storing the value to undo.
        self._obj.transform = self._base.transform.I * value

    transform = property(_wrapper_get_transform,_wrapper_set_transform)

    def __getattribute__(self,n):
        if n == '__class__':
            return self._wrapped_class
        elif n in ElementWrapper.__dict__:
            return object.__getattribute__(self,n)
        else:
            r = getattr(self._obj,n)
            if isinstance(r,ElementWrapper): 
                r = ElementWrapper(self._base,r)
            return r

    def __setattr__(self,n,v):
        if n in ElementWrapper.__dict__:
            object.__setattr__(self,n,v)
        else:
            setattr(self._obj,n,v)

    def __iter__(self):
        for v in self._obj:
            yield ElementWrapper(self._base,v)

    def iterlayout(self,*args,**kwargs):
        for l in self._obj.iterlayout(*args,**kwargs):
            yield ElementWrapper(self._base,l)

    def __getitem__(self,key):
        r = self._obj[key]
        if r == self._obj:
            return self
        else:
            r = ElementWrapper(self._base,r)
            return r

    def __enter__(self):
        return self._obj

    @non_evalable_repr_helper
    def __repr__(self):
        return {'id':str(self._base.id + self._obj.id)}
