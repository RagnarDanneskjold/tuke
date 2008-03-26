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

from __future__ import with_statement

from collections import deque
import weakref

import Tuke
import Tuke.context as context

def versions_compatible(cur,other):
    """Compare two versions and return compatibility.

    Evaluated under usual major.minor scheme.
    """

    try:
        # Enforce numerical versions, allowing strings and their ilk would be
        # way too confusing.
        for n in cur[0:2] + other[0:2]:
            if not isinstance(n,int):
                raise ValueError, 'Version major and minor must be ints: %s, %s' % (cur,other)
            elif n < 0:
                raise ValueError, 'Version major and minor must be greater than zero: %s, %s' % (cur,other)

        return cur[0] == other[0] and cur[1] >= other[1]
    except (TypeError, IndexError):
        raise ValueError, 'Invalid version: %s, %s' % (cur,other)

class Element(object):
    """Base element class.
    
    Everything is an Element, from a single pad on a pcb, to a whole circuit.
    This applies equally to things in schematic view and layout view. What is
    common to elements is as follows:

    They have an immutable Id

    That Id must have a single path component, IE, Id('foo/bar') is invalid.

    They can have one or more sub-elements, which must have unique Ids. They
    also have a parent, which may or may not be set.
    
    Try have a transform attribute, for geometry transformation data.

    They have a netlist attribute, for net list information.

    They can be loaded and saved to disk.
    """

    __required__ = ()
    __defaults__ = {'id':None,'transform':None,'connects':None}
    __version__ = (0,0)

    parent = context.Source(None)
    transform = context.Source(None)

    def _required_and_default_kwargs(self):
        """Return the required and default kwargs as a tuple."""

        req = set()
        d = {}
        for cls in reversed(self.__class__.__mro__):
            req.update(cls.__dict__.get('__required__',()))
            d.update(cls.__dict__.get('__defaults__',{}))

        return (req,d)

    def _repr_kwargs(self):
        """Return the list of kwargs needed to recreate the Element.
    
        This is all required arguments, and any default arguments who's values
        have changed from the default.
        """
        req,df = self._required_and_default_kwargs()

        kwargs = {}
        for k,v in df.items():
            if getattr(self,k) is not v:
                req.add(k)
                kwargs[k] = getattr(self,k)
        return kwargs 

    def __init__(self,**kwargs):
        # Initialize from kwargs
        #
        # All key/value pairs in kwargs will be added to self, self.key = value
        # Default arguments can be provided in defaults
        #
        # If a key is present in required, but not in kwargs, a TypeError will
        # be raised. If a key is present in kwargs, but not in required or
        # defaults, a TypeError will be raised.

        # Check that all versions are compatible.
        cls_version_required = self.__class__.__dict__.get('__version__',(0,0))
        cls_version_given = kwargs.get('__version__',cls_version_required)

        if not versions_compatible(cls_version_required,cls_version_given):
            raise TypeError, \
                    "Incompatible versions: got %s but need %s to create a %s" % \
                    (cls_version_given,cls_version_required,self.__class__)


        # Setup the dict with args from kwargs
        req,df = self._required_and_default_kwargs() 
       
        valid = req | set(df.keys())
        extra = set(kwargs.keys()).difference(valid)
        if extra:
            raise TypeError, 'Extra arguments %s' % str(extra)

        for k in req:
            try:
                setattr(self,k,kwargs[k])
            except KeyError:
                raise TypeError, 'Missing required argument %s' % k 

        for k,d in df.items():
            setattr(self,k,kwargs.get(k,d))

        # Call all the _init methods for all the classes.
        for cls in reversed(self.__class__.__mro__):
            if issubclass(cls,Element):
                cls._init(self)

    def _init(self):
        import Tuke
        if not self.id:
            self.id = Tuke.Id.random()
        else:
            self.id = Tuke.Id(self.id)

        if len(self.id) > 1:
            raise ValueError, 'Invalid Element Id \'%s\': more than one path component' % str(self.id)

        if self.transform is None:
            import Tuke.geometry
            self.transform = Tuke.geometry.Transformation()

        if self.connects is None:
            self.connects = Tuke.Connects()
        self.connects.base = self


    # Some notes on the sub-elements implementation:
    #
    # It can be assumed that there will be a *lot* of sub-element lookups, both
    # using foo.bar syntax, and foo[] So a dict that can quickly map id's to
    # elements of some sort is essential. Fortunately all Element objects have
    # their own ready made dict, __dict__ There is no reason why we can't put
    # anything we want in there, including sub-elements, so long as we're
    # careful to handle name collisions consistantly.

    def __iter__(self):
        """Iterate through sub-elements."""

        for i in self.__dict__.itervalues():
            if isinstance(i,Tuke.ElementRefContainer):
                yield i 

    def _element_id_to_dict_key(self,id):
        """Returns the dict key that Element id should be stored under.
        
        This is the key under which the Element of the given id will be stored
        under.
        """
        assert len(id) <= 1

        n = str(id)
        if hasattr(self,n) \
           and not isinstance(getattr(self,n),Tuke.ElementRefContainer):
            n = '_attr_collided_' + n
        return n

    def __getitem__(self,id):
        """Get element by Id

        Id can refer to subelements, or, if the Element has a parent, super
        elements. '../' refers to the parent for instance.
        """
        id = Tuke.Id(id)

        r = None
        if not id or id[0] == '..' or len(id) > 1:
            r = Tuke.ElementRef(self,id)
        else:
            r = self.__dict__[self._element_id_to_dict_key(id[0])]

        # Element[] should raise a KeyError immediately if the element doesn't exist, so force a dereference
        r._deref()
        return r

    class IdCollisionError(IndexError):
        pass

    def add(self,obj):
        """Add Element as sub-element.

        Returns the element, correctly wrapped.

        If the element's id is a valid Python identifier and there isn't
        already an attribute of that name, it will be accessible as self.(id)

        Raises Element.IdCollisionError on id collission.
        """
        if isinstance(obj,Tuke.ElementRef):
            raise TypeError, 'Can only add bare Elements, IE, foo.add(foo.bar) is invalid.'
        if not isinstance(obj,Element):
            raise TypeError, "Can only add Elements to Elements, not %s" % type(obj)

        if obj.parent:
            raise ValueError, "'%s' already has parent '%s'" % (obj,obj.parent)

        n = self._element_id_to_dict_key(obj.id)

        if hasattr(self,n):
            raise self.IdCollisionError,"'%s' already exists" % str(obj.id)

        obj.parent = self
        obj = Tuke.ElementRefContainer(self,obj)
        setattr(self,n,obj)

        return obj

    def iterlayout(self,layer_mask = None):
        """Iterate through layout.

        Layout iteration is done depth first filtering the results with the
        layer_mask. All geometry transforms are handled transparently.
        """
     
        # We can't import Tuke.geometry earlier, due to circular imports, hence
        # the weird layer_mask = None type junk.
        from Tuke.geometry import Layer
        if not layer_mask:
            layer_mask = '*'
        layer_mask = Layer(layer_mask)

        for s in self:
            from Tuke.geometry import Geometry
            if isinstance(s,Geometry):
                if s.layer in layer_mask:
                    yield s
            else:
                for l in s.iterlayout(layer_mask):
                    yield l


    class VersionError(ValueError):
        pass

    def __enter__(self):
        """Context manager support"""
        return self
    def __exit__(self,exc_type,exc_value,traceback):
        # reraise
        return False

    @Tuke.repr_helper
    def __repr__(self):
        kwargs = self._repr_kwargs() 
        return ((),kwargs)

    def _serialize(self,r,indent,root=False,full=False):
        r.append('%s%s = %s; ' % (indent,self.id,repr(self)))
        if not root:
            r.append('_.add(%s)\n' % (self.id))
        else:
            r.append('__root = %s\n' % (self.id))

        if not isinstance(self,ReprableByArgsElement) or full:
            subs = []
            for e in self: 
                if isinstance(e,Tuke.ElementRefContainer):
                    subs.append(e)
            subs.sort(key=lambda e: e.id)

            if subs:
                r.append('%swith %s as _:\n' % (indent,self.id))
                for e in subs:
                    with e as e:
                        e._serialize(r,indent + '    ')

    def serialize(self,full=False):
        """Serialize the Element and it's sub-Elements."""

        r = deque()

        r.append("""\
from __future__ import with_statement
import Tuke

""")

        self._serialize(r,'',root=True,full=full)

        return ''.join(r)


    def _apply_context(self,base):
        return ElementRef(self,base)

class ReprableByArgsElement(Element):
    """Base class for Elements fully representable by their arguments."""
    pass

class SingleElement(Element):
    """Base class for elements without subelements."""
    add = None
