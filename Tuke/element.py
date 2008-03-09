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
from xml.dom.minidom import Document,parse

class Element(object):
    """Base element class.
    
    Everything is an Element, from a single pad on a pcb, to a whole circuit.
    This applies equally to things in schematic view and layout view. What is
    common to elements is as follows:

    They have an immutable Id

    That Id must have a single path component, IE, Id('foo/bar') is invalid.

    They can have one or more sub-elements, which must have unique Ids.
    
    Try have a transform attribute, for geometry transformation data.

    They have a netlist attribute, for net list information.

    They can be loaded and saved to disk.
    """

    def __init__(self,id=None):
        from Tuke.geometry import Transformation
        from Tuke import Netlist

        if not id:
            id = Id.random()
        self.id = Id(id)

        if len(self.id) > 1:
            raise ValueError, 'Invalid Element Id \'%s\': more than one path component' % str(self.id)

        self.transform = Transformation()
        self.netlist = Netlist(id=self.id)

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
            if isinstance(i,subelement_wrapper):
                yield i

    def _element_id_to_dict_key(self,id):
        """Returns the dict key that Element id should be stored under.
        
        This is the key under which the Element of the given id will be stored
        under.
        """
        assert len(id) <= 1

        n = str(id)
        if hasattr(self,n) and not isinstance(getattr(self,n),subelement_wrapper):
            n = '_attr_collided_' + n
        return n

    def __getitem__(self,id):
        """Get sub-element by Id

        An alternative to the foo.bar lookups.
        """
        id = Id(id)

        if not len(id):
            raise KeyError, "Id('') is an invalid key"

        r = None
        try:
            r = self.__dict__[self._element_id_to_dict_key(id[0])]

            if len(id) > 1:
                r = subelement_wrapper(self,r[id[1:]])
        except KeyError:
            # Everything wrapped in a KeyError catch, so that inner KeyErrors
            # will give error messages relative to the outermost element.
            raise KeyError, "No sub-elements found matching '%s' in '%s'" % (str(id),str(self.id))

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

        if obj.__class__ == subelement_wrapper:
            raise TypeError, 'Can only add unwrapped Elements, IE, foo.add(foo.bar) is invalid.'

        if not isinstance(obj,Element):
            raise TypeError, "Can only add Elements to Elements, not %s" % type(obj)

        n = self._element_id_to_dict_key(obj.id)

        if hasattr(self,n):
            raise self.IdCollisionError,"'%s' already exists" % str(obj.id)

        obj = self._wrap_subelement(obj)
        setattr(self,n,obj)

        return obj

    def isinstance(self,cls):
        """Return isinstance(self,cls)

        Due to the behind the scenes element wrapping this must be used instead
        of isinstance.
        """
        return isinstance(self,cls)

    def save(self,doc):
        """Returns an XML minidom object representing the Element"""
        r = doc.createElement(self.__module__ + '.' + self.__class__.__name__)

        for n,v in self.__dict__.iteritems():
            if v.__class__  == subelement_wrapper: 
                r.appendChild(v.save(doc))
            else:
                r.setAttribute(n,repr(v))

        return r

    def _wrap_subelement(self,obj):
        """Wrap a subelement's id and transform attrs.

        Used so that a callee sees a consistant view of id and transform in
        sub-elements. For instance foo.bar.id == 'foo/bar'
        """

        return subelement_wrapper(self,obj)

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
            if s.isinstance(Geometry):
                if s.layer in layer_mask:
                    yield s
            else:
                for l in s.iterlayout(layer_mask):
                    yield l

    @non_evalable_repr_helper
    def __repr__(self):
        return {'id':str(self.id)}

class ElementRef(object):
    """A persistant pointer to an element.
    
    ElementRefs, once created, act almost identically to the original element
    in the same fashion as a weakref.proxy acts. The exceptions being that
    ref.__class__ is still ElementRef and repr() returns the string for a new
    ElementRef rather than the target elements repr. These changes are so the
    Element load and save code works.

    Note that ElementRefs are *not* weakrefs, and *will* increment the targets
    reference count.
    """

    class NotResolvedError(Exception):
        """ElementRef accessed before target resolved."""
        pass

    def __init__(self_real,target_id,target = None):
        """Create a ElementRef pointing to target
        
        target_id - What the target element's id should be stored as.
        target - The actual target Element obj, None if not yet available.

        ElementRef's can be created without target set, this is for load and
        save routines that may not have the Element instance that target refers
        to available at initalization.
        """
        self = lambda n: object.__getattribute__(self_real,n)

        object.__setattr__(self_real,'_ref_target_id',Id(target_id))

        self('set_target')(target)

    def set_target(self,target):
        """Set target object."""
        assert isinstance(target,(Element,subelement_wrapper,type(None)))

        object.__setattr__(self,'_ref_target',target)

    def __getattribute__(self_real,n):
        self = lambda n: object.__getattribute__(self_real,n)

        if n == '__class__':
            return self('__class__')
        elif n == '__repr__':
            return self('__repr__')
        else:
            if self('_ref_target') is None:
                if n == 'set_target':
                     return self('set_target')
                else:
                    raise ElementRef.NotResolvedError, 'ElementRef not yet resolved.'
            else:
                return getattr(self('_ref_target'),n)

    def __setattr__(self_real,n,v):
        setattr(object.__getattribute__(self_real,'_ref_target'),n,v)

    @repr_helper
    def __repr__(self):
        return ((object.__getattribute__(self,'_ref_target_id'),),{})


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
        return self._obj[key]

    @non_evalable_repr_helper
    def __repr__(self):
        return {'id':str(self._base.id + self._obj.id)}


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

    # Setup attributes
    for n,v in attr.iteritems():
        setattr(obj,n,v)

    # Finally load the add sub-elements, this must be done second, as add()
    # depends on the attributes id and transform
    for s in subs:
        obj.add(s)

    return obj

class _EmptyClass(object):
    pass

class SingleElement(Element):
    """Base class for elements without subelements."""
    add = None
    def __init__(self,id=Id()):
        Element.__init__(self,id=id)

def save_element_to_file(elem,f):
    """Save element to file object f"""

    doc = Document()

    f.write(elem.save(doc).toprettyxml(indent="  "))

def load_element_from_file(f):
    """Load the element represented by file object f"""

    doc = parse(f)

    e = load_Element(doc)
    return e
