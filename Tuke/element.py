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
from Tuke import Id,rndId,Netlist
from xml.dom.minidom import Document,parse


class Element(object):
    """Base element class.
    
    Everything is an Element, from a single pad on a pcb, to a whole circuit.
    This applies equally to things in schematic view and layout view. What is
    common to elements is as follows:
        
    They can be loaded and saved to disk.

    They have an immutable Id

    That Id must have a single path component, IE, Id('foo/bar') is invalid.
    """

    def __init__(self,id=''):
        from Tuke.geometry import Transformation
        self.id = Id(id)

        if len(self.id) != 1:
            raise ValueError, 'Invalid Element Id \'%s\': more than one path component' % str(self.id)

        self.transform = Transformation()

    def __iter__(self):
        """Iterate through sub-elements."""

        for v in self.__dict__.itervalues():
            if v.__class__ == subelement_wrapper:
                yield v

    def __getitem__(self,key):
        """Get sub-elements by Id

        Returns the list of matching sub-elements.
        """

        key = Id(key)
        r = [] 
        for v in self.__dict__.itervalues():
            if v.__class__ == subelement_wrapper \
               and v._obj.id == key[0]: 
                if len(key) > 1:
                    r += v[key[1:]]
                else:
                    r.append(v) 
        return r

    def add(self,obj):
        """Add Element as sub-element.

        If the element's id is a valid Python identifier and there isn't
        already an attribute of that name, it will be accessible as self.(id)
        """

        # Note that there is no actual test for valid identifiers... We said it
        # will not be accessible, not that it won't be in self.__dict__...
        n = str(obj.id)

        # If the id already exists have to come up with a fake name for it.
        if hasattr(self,n):
            n = str(rndId())

        setattr(self,n,
                self._wrap_subelement(self.id,self.transform,obj))

    def save(self,doc):
        """Returns an XML minidom object representing the Element"""
        r = doc.createElement(self.__module__ + '.' + self.__class__.__name__)

        for n,v in self.__dict__.iteritems():
            if v.__class__  == subelement_wrapper: 
                r.appendChild(v.save(doc))
            else:
                r.setAttribute(n,repr(v))

        return r

    def _wrap_subelement(self,base_id,base_transform,obj):
        """Wrap a subelement's id and transform attrs.

        Used so that a callee sees a consistant view of id and transform in
        sub-elements. For instance foo.bar.id == 'foo/bar'
        """

        return subelement_wrapper(base_id,base_transform,obj)

    def iterlayout(self,layer_mask = None,base_id = Id(), base_transform = None):
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

        if base_transform != None:
            base_transform = self.transform * base_transform
        else:
            base_transform = self.transform

        base_id = base_id + self.id
        for s in self:
            from Tuke.geometry import Geometry
            if isinstance(s,Geometry):
                if s.layer in layer_mask:
                    yield self._wrap_subelement(base_id,base_transform,s)
            else:
                for l in s.iterlayout(layer_mask,
                        base_id = base_id,
                        base_transform = base_transform):
                    yield l

class subelement_wrapper(object):
    """Class to wrap a sub-Element's id and transform attrs."""
    def __init__(self,base_id,base_transform,obj):
        self._base_id = base_id
        self._base_transform = base_transform
        self._obj = obj

    def _wrapper_get_id(self):
        return self._base_id + self._obj.id
    id = property(_wrapper_get_id)

    def _wrapper_get_transform(self):
        return self._base_transform * self._obj.transform
    def _wrapper_set_transform(self,value):
        # FIXME: life is far more complex than this...
        self._obj.transform = value

    transform = property(_wrapper_get_transform,_wrapper_set_transform)

    def __getattr__(self,n):
        r = getattr(self._obj,n)
        if r.__class__ == subelement_wrapper: 
            r = subelement_wrapper(self._base_id,self._base_transform,r)
        #print '__getattr__(%s,%s) -> %s' % (str(self._base_id + self._obj.id),n,repr(r))
        return r

    def __iter__(self):
        for v in self._obj:
            yield subelement_wrapper(self._base_id,self._base_transform,v)

    def __getitem__(self,key):
        r = self._obj[key]
        #print '__getitem__(%s,%s) -> %s' % (str(self._base_id + self._obj.id),key,repr([e.id for e in r]))
        return [subelement_wrapper(self._base_id,self._base_transform,e) for e in r]

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

    # Populate the subs first, to give any __setstate__ function possibly
    # needed info.
    obj.subs = subs

    # If the class defines __setstate__, let it handle the state, otherwise
    # just populate the object's dict. 
    if hasattr(obj,'__setstate__'):
        obj.__setstate__(attr)
    else:
        for n,v in attr.iteritems():
            setattr(obj,n,v)

    return obj

class _EmptyClass(object):
    pass

class SingleElement(Element):
    """Base class for elements without subelements."""
    __iter__ = None
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
