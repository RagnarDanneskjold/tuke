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

    __version__ = (0,0)

    def __init__(self,id=None):
        """Initialize an Element"""

        from Tuke.geometry import Transformation

        if not id:
            id = Tuke.Id.random()
        self.id = Tuke.Id(id)

        if len(self.id) > 1:
            raise ValueError, 'Invalid Element Id \'%s\': more than one path component' % str(self.id)

        self.transform = Transformation()

        self.connects = Tuke.Connects(base=self)

        self._parent = None
        self.parent_change_callbacks = weakref.WeakKeyDictionary()

    def _parent_setter(self,v):
        self._parent = v

        old_callbacks = self.parent_change_callbacks
        self.parent_change_callbacks = weakref.WeakKeyDictionary()

        for obj,fn in old_callbacks.iteritems():
            fn(obj)
    parent = property(lambda self: self._parent,_parent_setter)

    parent_change_callbacks = None
    """Parent change callback.

    This is a WeakKeyDictionary who's values will be called with the keys as
    the argument when ever parent changes. Before the callbacks are run
    parent_change_callback is reset to an empty WeakKeyDictionary. If the
    callback still needs to monitor parent, it must add another callback.
    
    The logic behind this is sometimes you want to know when the topology of
    the Element graph changes. So you setup callbacks in the correct place
    which when called update whatever it is that needs to be updated. It's
    implemented as a WeakKeyDictionary so that callbacks don't get left around
    when the object that needs them changes. Finally for convenience the object
    that needed the callback is passed to the function, often preventing the
    need to create closures.
    
    """

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
        if not id:
            return self
        elif id[0] == '..' or len(id) > 1:
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

    @staticmethod
    def _basic_version_check(cur,other):
        """Basic major/minor version check.

        cur - Current version.
        other - Version being checked.
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

    class VersionError(ValueError):
        pass

    def __enter__(self):
        """Context manager support"""
        return self
    def __exit__(self,exc_type,exc_value,traceback):
        # reraise
        return False

    @classmethod 
    def from_older_version(cls,other):
        if not cls == other.__class__:
            raise TypeError, 'Got %s, expected %s in from_older_version()' % (cls,other.__clss__)
        elif not cls._basic_version_check(cls.__version__,other.__version__):
            raise cls.VersionError, '%s is an incompatible version of %s, need %s' % (other.__version__,cls,cls.__version__)
        else:
            return other

    @Tuke.repr_helper
    def __repr__(self):
        kwargs = self._get_kwargs()
        return ((),kwargs)

    def _get_kwargs(self,a_kwargs = {}):
        """Return the kwargs required to represent the Element
        
        Subclasses should define this function, have have it call their base
        classes _get_kwargs(), adding additional kwargs to the dict as needed.

        """

        kwargs = {'id':self.id}
        kwargs.update(a_kwargs)

        return kwargs 

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


class ReprableByArgsElement(Element):
    """Base class for Elements representable by their arguments."""

    def __init__(self,kwargs,required=(),defaults={}):
        """Initialize from kwargs

        All key/value pairs in kwargs will be adde to self.__dict__ Default
        arguments can be provided in defaults
        
        If a key is present in required, but not in kwargs, a TypeError will be
        raised. If a key is present in kwargs, but not in required or defaults,
        a TypeError will be raised.
        """

        Element.__init__(self,id=kwargs.get('id',''))

        self._kwargs_keys = kwargs.keys()

        d = {'id':''}
        d.update(defaults)
        defaults = d

        kw = defaults.copy()
        kw.update(kwargs)
        try:
            del kw['id']
        except KeyError:
            pass

        required = set(required)
        valid = required | set(defaults.keys())

        if set(kwargs.keys()) & required != required:
            raise TypeError, 'Missing required arguments %s' % str(required.difference(set(kwargs.keys())))

        extra = set(kwargs.keys()).difference(valid)
        if extra:
            raise TypeError, 'Extra arguments %s' % str(extra)

        self.__dict__.update(kw)

    def _get_kwargs(self,a_kwargs = {}):
        kwargs = {}
        for k in self._kwargs_keys:
            kwargs[k] = self.__dict__[k]

        kwargs.update(a_kwargs)
        return Element._get_kwargs(self,kwargs)


class SingleElement(Element):
    """Base class for elements without subelements."""
    add = None
