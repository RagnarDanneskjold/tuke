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

from Tuke.geometry import V,Transformation

# Cache of ElementRefs.
#
# A WeakKeyDict, where the keys are the base Element objects, and the values
# are WeakValueDictionaries, with the Id's as keys and the values being the
# cached ElementRefs.
import weakref
ElementRef_cache = weakref.WeakKeyDictionary()

class ElementRefError(KeyError):
    """Referenced Element not found
    
    The stack of partially dereferenced Elements is available in partial_stack,
    starting from base and ending at the last Element found.
    """
    def __init__(self,msg,partial_stack):
        self.msg = msg

        # Under some circumstances with ../ references a None can be added to
        # the end of the stack, remove it.
        if partial_stack[-1] is None:
            partial_stack.pop()

        self.partial_stack = partial_stack

    def __str__(self):
        return self.msg

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

    # Id is a neat exception. It doesn't need wrapping, because, it's the bit
    # of information that defines what wrapping needs to be done.
    id = None

    # See Connects code for all the gory details. In short, since there is one,
    # and only one, ElementRef object for each base/ref combo each explicit
    # connection maps to one ElementRef object. This key is then used to help
    # implement the *implicit* connectivity map, and is defined here for the
    # above __getattribute__ magic reasons.
    _implicit_connectivity_key = None

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

    def _get_ref_stack(self):
        """Get the stack of referenced elements, from base to ref"""
        id = self.id
        r = [self._base]
        try:
            while id:
                if id[0] == '..':
                    r.append(r[-1].parent)
                else:
                    r.append(r[-1].__dict__[r[-1]._element_id_to_dict_key(id[0])])
                    if isinstance(r[-1],ElementRefContainer):
                        r[-1] = object.__getattribute__(r[-1],'_elem')
                id = id[1:]
            # If id == '..' while will run out of id to check and r will have a
            # None added to it due to the None parent, but this won't actually
            # get checked by anything except the following.
            if r[-1] is None:
                raise KeyError
            return r
        except KeyError:
            raise ElementRefError, \
                ("'%s' not found in '%s'" % (str(self.id),str(self._base.id)), r)
        except AttributeError:
            raise ElementRefError, \
                ("'%s' not found in '%s', ran out of parents at '%s'" %\
                (str(self._base.id),str(self.id),
                        str(self.id[0:\
                            len(self.id) - len(id)])), r)

    def _deref(self):
        """Return referenced Element object."""
        return self._get_ref_stack()[-1]

    def _unwrap_data_in(self,v):
        """Unwrap incoming data.

        This translates the context from self._base to self._deref()
        """

        if isinstance(v,Id):
            return v.relto(self.id)
        elif isinstance(v,ElementRef):
            if self._base is v._base:
                return ElementRef(self._deref(),v.id.relto(self.id))
            else:
                return v
        elif isinstance(v,Transformation):
            st = self._get_ref_stack()
            t = st[0].transform
            for e in st[1:-1]:
                t = t * e.transform
            return t.I * v
        elif isinstance(v,V):
            st = self._get_ref_stack()
            t = st[0].transform
            for e in st[1:]:
                t = t * e.transform
            return t.I(v)
        elif isinstance(v,(tuple,list)):
            return type(v)([self._wrap_data_in(i) for i in v])
        else:
            return v

    def _wrap_data_out(self,r):
        """Wrap outgoing data.
        
        This translates the context from self._deref() to self._base
        """
        import types

        if isinstance(r,Id):
            return self.id + r 
        elif isinstance(r,ElementRef):
            if r._base is self._deref():
                return ElementRef(self._base,self.id + r.id)
            else:
                return r
        elif isinstance(r,Transformation):
            st = self._get_ref_stack()
            t = st[0].transform
            for e in st[1:-1]:
                t = t * e.transform
            return t * r
        elif isinstance(r,V):
            st = self._get_ref_stack()
            t = st[0].transform
            for e in st[1:]:
                t = t * e.transform
            return t(r)
        elif isinstance(r,(tuple,list)):
            return type(r)([self._wrap_data_out(i) for i in r])
        elif isinstance(r,(types.GeneratorType)):
            # Generator objects, for instance iterlayout() will use this. The
            # above test is a bit limited though, iter((1,2,3)) is *not* a
            # GeneratorType for instance.
            class GeneratorWrapper(object):
                def __init__(self,ref,r):
                    self.ref = ref
                    self.r = r
                def __iter__(self):
                    return self
                def next(self):
                    return self.ref._wrap_data_out(self.r.next())
            return GeneratorWrapper(self,r)
        elif isinstance(r,types.MethodType):
            # Bound methods have their arguments and returned value wrapped.
            # This is done by returning a callable object wrapping the method.
            class MethodWrapper(object):
                def __init__(self,ref,fn):
                    self.ref = ref
                    self.fn = fn
                def __call__(self,*args,**kwargs):
                    args = [self.ref._unwrap_data_in(i) for i in args]
                    for k in kwargs.keys():
                        kwargs[k] = self.ref._unwrap_data_in(kwargs[k])
                    r = self.fn(*args,**kwargs)
                    r = self.ref._wrap_data_out(r)
                    return r
            return MethodWrapper(self,r)
        else:
            return r

    def __getattribute__(self,n):
        if n == '__class__':
            return type('ElementRef',
                        (ElementRef,self._deref().__class__),
                        {})
        elif n in ElementRef.__dict__:
            return object.__getattribute__(self,n)
        else:
            r = getattr(self._deref(),n)
            return self._wrap_data_out(r)

    def __setattr__(self,n,v):
        if n in ElementRef.__dict__:
            object.__setattr__(self,n,v)
        else:
            setattr(self._deref(),n,self._unwrap_data_in(v))

    def __getitem__(self,k):
        return self._wrap_data_out(self._deref().__getitem__(k))

    def __iter__(self):
        for i in iter(self._deref()):
            yield self._wrap_data_out(i) 

    def __enter__(self):
        return self._deref()

    @non_evalable_repr_helper
    def __repr__(self):
        return {'id':str(self.id),'base':str(self._base.id)}

class ElementRefContainer(ElementRef):
    """An ElementRef where the 'ref' is also the container for the Element
    
    Used to store sub-Elements of Elements.
    """
    def __new__(cls,base,elem):
        self = super(ElementRefContainer,cls).__new__(cls,base,elem.id)

        object.__setattr__(self,'_elem',elem)

        return self

    def _deref(self):
        return object.__getattribute__(self,'_elem')
