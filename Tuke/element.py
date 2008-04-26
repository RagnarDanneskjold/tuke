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

import Tuke.repr_helper

import Tuke
import Tuke.context as context
import Tuke.context.wrapped_str_repr

import Tuke.repr_helper
from Tuke.context.wrapper import unwrap

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

class Element(context.source.Source):
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

        # Find changed defaults
        kwargs = {}
        for k,v in df.items():
            if getattr(self,k) is not v:
                req.add(k)
                kwargs[k] = getattr(self,k)

        # Add in required
        for r in req:
            kwargs[r] = getattr(self,r)
        return kwargs 

    def __new__(cls,**kwargs):
        from Tuke.geometry import Transformation
        self = context.source.Source.__new__(cls,
                Tuke.Id('.'),
                Transformation(),
                None)

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
        return context.wrapper.wrap(self,self)

    def _init(self):
        import Tuke
        # Note how _*_real is used here.
        if not self._id_real:
            self.id = Tuke.Id.random()
        else:
            self.id = Tuke.Id(self._id_real)

        if len(self._id_real) > 1:
            raise ValueError, 'Invalid Element Id \'%s\': more than one path component' % str(self.id)

        if self._transform_real is None:
            import Tuke.geometry
            self.transform = Tuke.geometry.Transformation()

        self._notify_callbacks = {}
        if self.connects is None:
            self.connects = Tuke.Connects()
        self.connects.parent = self

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
            if isinstance(i,Element):
                yield i 

    def _element_id_to_dict_key(self,id):
        """Returns the dict key that Element id should be stored under.
        
        This is the key under which the Element of the given id will be stored
        under.
        """
        assert len(id) <= 1

        n = str(id)
        if hasattr(self,n) \
           and not isinstance(getattr(self,n),Element):
            n = '_attr_collided_' + n
        return n

    def __getitem__(self,id):
        """Get element by Id

        Id can refer to subelements, or, if the Element has a parent, super
        elements. '../' refers to the parent for instance.
        """
        id = Tuke.Id(id)

        if not id:
            return self
        else:
            r = None
            if id[0] == Tuke.Id('..'):
                if self.parent is not None:
                    r = self.parent
                else:
                    raise KeyError("Element '%s' has no parent" % self._id_real)
            else:
                try:
                    r = self.__dict__[self._element_id_to_dict_key(id[0])]
                except KeyError:
                    raise KeyError("'%s' is not a sub-Element of '%s'" %
                                    (id,self._id_real))
            if len(id) > 1:
                return r[str(id[1:])]
            else:
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

        # NOTE: Element.add is special cased by the wrapper code. obj does not
        # have the wrapping context removed from it like normal. See wrapper.c
        # for details.
        if not isinstance(obj,Element):
            raise TypeError, "Can only add Elements to Elements, not %s" % type(obj)

        if obj.parent:
            raise ValueError, "'%s' already has parent '%s'" % (obj,obj.parent)

        n = self._element_id_to_dict_key(obj.id)

        if hasattr(self,n):
            raise self.IdCollisionError,"'%s' already exists" % str(obj.id)

        obj.parent = self
        obj._call_notify_callbacks(Tuke.Id('.'))
        setattr(self,n,obj)

        self._call_notify_callbacks(obj.id)

        return obj

    def _call_notify_callbacks(self,filter):
        try:
            cb = self._notify_callbacks[filter]
        except KeyError:
            return

        del self._notify_callbacks[filter]
        for c in cb:
            c = c()
            if c is not None:
                c()

    def notify(self,filter,callback):
        """Notify on topology changes.

        filter - Path to filter by, must be a single path segment, either
                 referring to a sub-element, or referring to the parent, Id('..')

        callback - The callback. A weakref if callable is made, a reference to
                   callable must be kept elsewhere.

        The callbacks are one-shot, after they are called they are removed. The
        callback may call notify again however.

        """
        if not filter:
            raise ValueError(
                    "Filter '%s' invalid" % repr(filter))
        if len(filter) != 1:
            raise ValueError(
                    "Filter must have exactly one path segment, not '%s'" %
                    repr(filter))
        if not callable(callback):
            raise TypeError(
                    "'%s' is not callable" % repr(callback))

        # A WeakValueDictionary could be used here, except that we need to
        # store multiple callbacks for a given filter key. Hence this dict of
        # sets, where if all the weakrefs in the set go away, the set does too.
        def mkremover(filter):
            self_ref = weakref.ref(self)
            def r(callback_ref):
                self = self_ref()
                if self is not None:
                    # The garbage collector may call us after notify_callbacks
                    # has been reset, to catch any KeyErrors
                    try:
                        self._notify_callbacks[filter].remove(callback_ref)
                        if not self._notify_callbacks[filter]:
                            del self._notify_callbacks[filter]
                    except KeyError:
                        pass
            return r
        remover = mkremover(filter)

        # The unwrap is a subtle, but very important point. The callback may be
        # wrapped, if it is, then the only reference to the *wrapper* object is
        # here, and will be immediately garbage collected even though the
        # unwrapped callback is still alive.
        callback_ref = weakref.ref(unwrap(callback),remover)

        try:
            self._notify_callbacks[filter].add(callback_ref)
        except KeyError:
            self._notify_callbacks[filter] = set((callback_ref,))

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

    def _common_parent(self,b):
        a = unwrap(self)
        b = unwrap(b)

        ap = set()
        bp = set()

        while ((not ap.intersection(bp))) and \
               (a is not None or b is not None):
            if a is not None:
                ap.add(a)
                a = unwrap(a.parent)
            if b is not None:
                bp.add(b)
                b = unwrap(b.parent)
        p = ap.intersection(bp)
        if p:
            assert(len(p) == 1)
            return p.pop()
        else:
            return None

    def have_common_parent(self,b):
        """Determine if self and b have a common parent.

        For the purposes of the calculation, self and b are considered to be
        parents of themselves, given the graph a->b->c->d
        a.have_common_parent(a.b.c.d) would return True.
        """
        if self._common_parent(b) is not None:
            return True
        else:
            return False

    class VersionError(ValueError):
        pass

    # Element.__enter__() is special-cased by the wrapper code and is fully
    # implemented there. See wrapper.c for details.
    #def __enter__(self):
    #    """Context manager support"""
    #    return self
    def __exit__(self,exc_type,exc_value,traceback):
        # reraise
        return False

    @Tuke.repr_helper.wrapped_repr_helper
    def __wrapped_repr__(self):
        kwargs = self._repr_kwargs() 
        return ((),kwargs)
    __repr__ = Tuke.context.wrapped_str_repr.unwrapped_repr

    def serialize(self,
                  f,
                  full=False,
                  indent=None,
                  level=0):
        """Serialize the Element and it's sub-Elements."""

        if indent is None:
            f.write("""\
from __future__ import with_statement
import Tuke

""")
            indent = []
            self.serialize(f,full,indent=[],level=0)
        else:
            def out(s):
                for i in indent:
                    f.write(i)
                f.write(s)

            from Tuke.repr_helper import shortest_class_name
            cname = shortest_class_name(self.__class__)
            s = '%s = %s(' % (self._id_real,cname)
            out(s)
            indent.append(' ' * len(s))

            kw = self._repr_kwargs()
            kw['id'] = self._id_real
            kw['transform'] = self._transform_real

            first = True
            for n,v in kw.iteritems():
                if not first:
                    f.write(',\n')
                    out('%s=%s' % (n,repr(v)))
                else:
                    first = False
                    f.write('%s=%s' % (n,repr(v)))

            f.write('); ')
            if level > 0:
                f.write('__%d.add(%s)\n' % (level,self._id_real))
            else:
                f.write('__%d = %s\n' % (level,self._id_real))
            indent.pop()

            if not isinstance(self,ReprableByArgsElement) or full:
                subs = []
                for e in self: 
                    if isinstance(e,Element):
                        subs.append(e)
                subs.sort(key=lambda e: e.id)

                if subs:
                    out('with %s as __%d:\n' % (self._id_real,level + 1))
                    for e in subs:
                        unwrap(e).serialize(f,full,
                                            indent=indent + ['    ',],
                                            level=level + 1)

class ReprableByArgsElement(Element):
    """Base class for Elements fully representable by their arguments."""
    pass

class SingleElement(Element):
    """Base class for elements without subelements."""
    add = None
