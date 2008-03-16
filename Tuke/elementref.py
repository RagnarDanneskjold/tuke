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


from Tuke import Element,Id,non_evalable_repr_helper

# Cache of ElementRefs.
#
# A WeakKeyDict, where the keys are the base Element objects, and the values
# are WeakValueDictionaries, with the Id's as keys and the values being the
# cached ElementRefs.
import weakref
ElementRef_cache = weakref.WeakKeyDictionary()

class ElementRefError(KeyError):
    """Referenced Element not found"""
    pass

class ElementRef(object):
    """Reference an Element from a given context.

    Why from a given context? Well, the context is what determines what the
    referenced Element is. For instance, in the context of 'a', 'b' is a
    different thing if a.b is deleted and replaced. So an ElementRef only
    stores a reference to the Element providing the context, and the Id of the
    wrapped Element.

    The second function of an ElementRef is to transform various parts of the
    referened Element so as to be consistant from the referencing context. A
    simple example is the Id. For instance if 'a' is referencing sub-element
    'b' the ElementRef object a.b would have an .id of 'a/b' Similarly if b is
    translated by (1,1), sub-elements of b should have their geometry
    transformed as well, from a's perspective. Through bits of
    __getattribute__-style magic this is achieved.

    It's quite possible for the referenced Element to reference it's parent,
    for instance '..' In that case the transformations applied are the inverse
    of the context applied by the context.

    ElementRefs are resolved at run-time, each attribute access triggers a
    complete dereferencing/translation operation of the attribute. This also
    means that an ElementRef does not increment the refcount of the referenced
    Element. If a referenced Element isn't available, a ElementRefError will be
    raised.

    isinstance(ref,ElementRef) == True, and 
    isinstance(ref,referenced element.__class__/base classes) == True

    ElementRefs are context managers, and can be used with the with statement
    as follows:

    a = Element('a')
    a.add(Element('b')
    with a.b as b:
        # do stuff with b, in the context of b
    """

    # Since isinstance(e,Element) must work ElementRefs are implemented using
    # __getattribute__ Except for __class__ accesses the logic is quite simple,
    # if name is in ElementRef.__dict__, return self.name, otherwise,
    # referenced.name Therefore the following names must be declared in the
    # class context.
    _base = None

    # Id is a nifty special case. The reference *is* the Id, from the contexts
    # perspective, no wrapping needed.
    id = None

    def __new__(cls,base,id):
        """Create a new ElementRef

        base - Context providing Element 
        id - Referenced Element Id

        A subtle point is that for any given base/id only one
        ElementRef object will be created, subsequent calls will return
        the same object. This is required not just for performence reasons, but
        to maintain the following invarient:
        
        c2 = a.b.c
        c2 is a.b.c
        """

        id = Id(id)

        try:
            return ElementRef_cache[base][id]
        except KeyError:
            self = object.__new__(cls)

            assert(isinstance(base,Element))
            self._base = base
            self.id = id

            try: 
                ElementRef_cache[base][id] = self
            except KeyError:
                ElementRef_cache[base] =\
                        weakref.WeakValueDictionary()
                ElementRef_cache[base][id] = self

            return self

    def _deref(self):
        """Return referenced Element object."""
        id = self.id
        r = self._base
        try:
            while id:
                if id[0] == '..':
                    r = r.parent
                else:
                    r = r.__dict__[r._element_id_to_dict_key(id[0])]
                id = id[1:]
            return r
        except KeyError:
            raise ElementRefError, \
                "'%s' not found in '%s'" % (str(self._base.id),str(self.id))
        except AttributeError:
            raise ElementRefError, \
                "'%s' not found in '%s', ran out of parents at '%s'" %\
                (str(self._base.id),str(self.id),
                        str(self.id[0:\
                            len(self.id) - len(id)]))

    def add(self,obj):
        return ElementRef(self._base,
                self.id + self._deref().add(obj).id)

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
            return type('ElementRef',
                        (ElementRef,self._deref().__class__),
                        {})
        elif n in ElementRef.__dict__:
            return object.__getattribute__(self,n)
        else:
            r = getattr(self._deref(),n)
            return r

    def __setattr__(self,n,v):
        if n in ElementRef.__dict__:
            object.__setattr__(self,n,v)
        else:
            setattr(self._deref(),n,v)

    def __enter__(self):
        return self._deref()

    @non_evalable_repr_helper
    def __repr__(self):
        return {'id':self.id}
