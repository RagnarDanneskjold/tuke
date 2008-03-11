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

# Cache of subelement_wrappers, stored with (id(base),id(obj)) as keys.
#
# Possible bug... Could potentially return a value, if base and object are both
# deleted and others end up at the same address, seems unlikely though.
import weakref
subelement_wrapper_cache = weakref.WeakValueDictionary()

class subelement_wrapper(object):
    """Class to wrap a sub-Element's id and transform attrs.
    
    This is the magic that allows foo.bar.id to be 'foo/bar', even though
    seperately foo.id == 'foo' and bar.id == 'bar'

    """
    def __new__(cls,base,obj):
        """Create a new subelement_wrapper

        base - base element
        obj - wrapped element

        A subtle point is that for any given (id(base),id(obj)) only one
        subelement_wrapper object will be created, subsequent calls will return
        the same object. This is required not just for performence reasons, but
        to maintain the following invarient:
            
        a.b.add(Element('c')) == a.b.c
        """

        cache_key = (id(base),id(obj))
        try:
            return subelement_wrapper_cache[cache_key]
        except KeyError:
            self = super(subelement_wrapper,cls).__new__(cls)

            assert(isinstance(base,Element))
            assert(isinstance(obj,(Element,subelement_wrapper)))
            object.__setattr__(self,'_base',base)
            object.__setattr__(self,'_obj',obj)

            subelement_wrapper_cache[cache_key] = self
            return self

    def isinstance(self,cls):
        return self._obj.isinstance(cls)

    def add(self,obj):
        return subelement_wrapper(self._base,
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

    def __getattr__(self,n):
        r = getattr(self._obj,n)
        if r.__class__ == subelement_wrapper: 
            r = subelement_wrapper(self._base,r)
        return r

    def __setattr__(self,n,v):
        # Ugh, this is really ugly.
        #
        # For __getattr__ the transform property is called as you would expect,
        # but __setattr__ bypasses this, so we have to handle it manually.
        if n != 'transform':
            setattr(self._obj,n,v)
        else:
            self._wrapper_set_transform(v) 

    def __iter__(self):
        for v in self._obj:
            yield subelement_wrapper(self._base,v)

    def iterlayout(self,*args,**kwargs):
        for l in self._obj.iterlayout(*args,**kwargs):
            yield subelement_wrapper(self._base,l)

    def __getitem__(self,key):
        r = self._obj[key]
        if r == self._obj:
            return self
        else:
            return r

    @non_evalable_repr_helper
    def __repr__(self):
        return {'id':str(self._base.id + self._obj.id)}
