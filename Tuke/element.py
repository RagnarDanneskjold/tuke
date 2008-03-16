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

import Tuke
from Tuke import Id,rndId,Netlist,repr_helper,non_evalable_repr_helper
from repr_helper import shortest_class_name
from xml.dom.minidom import Document,parse

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
        from Tuke import Netlist

        if not id:
            id = Id.random()
        self.id = Id(id)

        if len(self.id) > 1:
            raise ValueError, 'Invalid Element Id \'%s\': more than one path component' % str(self.id)

        self.transform = Transformation()
        self.netlist = Netlist(id=self.id)


        self._parent = None
        self.parent_set_callback = []
        self.parent_unset_callback = []

    def _parent_setter(self,v):
        if v is None:
            for c in self.parent_unset_callback:
                c(self)
            self._parent = None
        else:
            self._parent = v
            for c in self.parent_set_callback:
                c(self)
    parent = property(lambda self: self._parent,_parent_setter)

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
        id = Id(id)

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

    def save(self,doc):
        """Returns an XML minidom object representing the Element"""
        r = doc.createElement(shortest_class_name(self.__class__))

        for n,v in self.__dict__.iteritems():
            if n in set(('parent','_parent','parent_set_callback','parent_unset_callback')):
                continue
            if isinstance(v,Element): 
                r.appendChild(v.save(doc))
            else:
                r.setAttribute(n,repr(v))

        return r

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

    @repr_helper
    def __repr__(self):
        kwargs = self._serialize()
        return ((),kwargs)

    def _serialize(self,a_kwargs = {}):
        """Return the kwargs required to represent the Element
        
        Subclasses should define this function, have have it call their base
        classes _serialize(), adding additional kwargs to the dict as needed.

        """

        kwargs = {'id':self.id}
        kwargs.update(a_kwargs)

        return kwargs 

    def serialize(self):
        """Serialize the Element and it's sub-Elements."""

        return r

def load_Element(dom):
    """Loads elements from a saved minidom"""


    # Since the xml is saved as a tree, and elements depend on their
    # subelements, the load operation must be done in a depth-first recursive
    # manner.

    subs = []
    for sub in dom.childNodes:
        s = load_Element(sub)
        if s:
            subs.append(s)

    # An actual dom from the disk will include a number of node types we don't
    # need, like text nodes and comment nodes, ignore everything but element
    # nodes.
    if dom.nodeType != dom.ELEMENT_NODE:
        if dom.nodeType == dom.DOCUMENT_NODE:
            # Ooops, special case here. The dom is wrapped by a
            # "document_node", which has children that we need to return.
            assert len(subs) == 1
            return subs[0]
        return None 
    
    # De-repr() the element attributes to generate a dict.
    attr = {}
    for n,v in dom.attributes.items():
        v = eval(v)
        attr[n] = v


    # Create an instance of the class referred to by the tagName
    import sys

    # First split up the module part of tagName from the trailing class part.
    module = dom.tagName.split('.')
    name = module[-1]
    module = reduce(lambda a,b: a + '.' + b,module[0:-1])

    # Load the required module and get the correct class object.
    __import__(module)

    mod = sys.modules[module]
    
    klass = getattr(mod,name)
   
    # Create a new object of the correct class.
    #
    # Not really sure why obj = object() doesn't work, gives an odd error:
    # "__class__ assignment: only for heap types"
    obj = _EmptyClass() 
    obj.__class__ = klass

    # FIXME: ugly hack, will go away when we make non-xml switch to eval()able
    # representations.
    obj.parent_set_callback = []
    obj.parent_unset_callback = []
    obj._parent = None

    # Setup attributes
    for n,v in attr.iteritems():
        setattr(obj,n,v)

    # Finally load the add sub-elements, this must be done second, as add()
    # depends on the attributes id and transform
    for s in subs:
        obj.add(s)

    return obj

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

    def _serialize(self,a_kwargs = {}):
        kwargs = {}
        for k in self._kwargs_keys:
            kwargs[k] = self.__dict__[k]

        kwargs.update(a_kwargs)
        return Element._serialize(self,kwargs)


class SingleElement(Element):
    """Base class for elements without subelements."""
    add = None


class _EmptyClass(object):
    pass


def save_element_to_file(elem,f):
    """Save element to file object f"""

    doc = Document()

    f.write(elem.save(doc).toprettyxml(indent="  "))

def load_element_from_file(f):
    """Load the element represented by file object f"""

    doc = parse(f)

    e = load_Element(doc)
    return e
