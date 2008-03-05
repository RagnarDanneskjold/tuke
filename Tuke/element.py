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
from Tuke import Id,rndId,Netlist,non_evalable_repr_helper
from xml.dom.minidom import Document,parse


class Element(object):
    """Base element class.
    
    Everything is an Element, from a single pad on a pcb, to a whole circuit.
    This applies equally to things in schematic view and layout view. What is
    common to elements is as follows:
        
    They can be loaded and saved to disk.

    They have an immutable Id

    That Id must have a single path component, IE, Id('foo/bar') is invalid.

    They can have one or more sub-elements.
    """

    def __init__(self,id=''):
        from Tuke.geometry import Transformation
        self.id = Id(id)

        if len(self.id) > 1:
            raise ValueError, 'Invalid Element Id \'%s\': more than one path component' % str(self.id)

        self.transform = Transformation()

    # Some notes on the sub-elements implementation:
    #
    # It can be assumed that there will be a *lot* of sub-element lookups, both
    # using foo.bar syntax, and foo[] So a dict that can quickly map id's to
    # elements of some sort is essential. Fortunately all Element objects have
    # their own ready made dict, __dict__ There is no reason why we can't put
    # anything we want in there, including sub-elements, so long as we're
    # careful to handle name collisions consistantly.
    #
    # The rules for nam collisions are pretty simple. If the collision is with
    # an existing set of subelements, just add the new element to that set. If
    # it's with an existing Element, convert to a subelement_set containing
    # both. Finally, if the name is used by a non-subelement-related attribute,
    # re-try the above but using a strong hash of the name instead.


    def __iter__(self):
        """Iterate through sub-elements."""

        for i in self.__dict__.itervalues():
            if i.__class__ == subelement_wrapper:
                yield i
            elif i.__class__ == subelement_set:
                for j in i:
                    yield j

    def _element_id_to_dict_key(self,id):
        """Returns the dict key that Element id should be stored under.
        
        This is the key under which the Element of the given id will be stored
        under.
        """
        assert len(id) <= 1

        n = str(id)
        if hasattr(self,n) and not isinstance(getattr(self,n),(subelement_set,subelement_wrapper)):
            # hash(str) would be nice to use, but the documentation only says that
            # hash collisions are unlikely, rather than crypto-unlikely.
            #
            # md5 and sha on Python are both basically the same speed. md5 however
            # results in shorter strings, so we use it. hexdigest() is slightly
            # slower than digest(), but it's really not significant.
            import md5
            n = md5.new(n).hexdigest()
        return n

    def __getitem__(self,id):
        """Get sub-element by Id

        Similar to byid(), but raises a LookupError if there are multiple
        sub-elements with the same id
        """
        r = self.byid(id)

        if len(r) > 1:
            raise LookupError, "Multiple sub-elements match '%s'" % str(id)

        return r.pop()

    def byid(self,key):
        """Get sub-elements by Id

        Returns the set of matching sub-elements. Raises KeyError if there are
        no matches.
        """
        print "byid for '%s' in '%s'" % (str(key),str(self.id))
        key = Id(key)

        if not len(key):
            raise KeyError, 'byid(Id()) will always match nothing'

        # Note the pattern of r = subelement_set(), this is to pass through to
        # the final raise KeyError at the bottom.
        try:
            r = self.__dict__[self._element_id_to_dict_key(key[0])]
        except KeyError:
            r = subelement_set()

        if not isinstance(r,(subelement_set,subelement_wrapper)):
            r = subelement_set() 

        if not isinstance(r,subelement_set):
            r = subelement_set((r,))

        if len(key) > 1:
            j = r
            r = set()
            for i in j:
                try:
                    # This is a search, which may fail, if so, ignore. 
                    r |= i.byid(key[1:])
                except KeyError:
                    pass

        if not r:
            raise KeyError, "No sub-elements found matching '%s' in '%s'" % (str(key),str(self.id))

        return r

    def add(self,obj):
        """Add Element as sub-element.

        Returns the element, correctly wrapped.

        If the element's id is a valid Python identifier and there isn't
        already an attribute of that name, it will be accessible as self.(id)

        Element id collisions, when there wasn't an attribute of the same name,
        will result in self.foo returning a set.
        """

        if obj.__class__ == subelement_wrapper:
            raise TypeError, 'Can only add unwrapped Elements, IE, foo.add(foo.bar) is invalid.'

        if not isinstance(obj,Element):
            raise TypeError, "Can only add Elements to Elements, not %s" % type(obj)

        n = self._element_id_to_dict_key(obj.id)

        obj = self._wrap_subelement(obj)

        if not hasattr(self,n):
            # Simple case, attribute doesn't already exist.
            setattr(self,n,obj)
        else:
            if isinstance(getattr(self,n),subelement_set):
                # Already a set by that name
                setattr(self,n,
                        getattr(self,n).add(obj))
            elif isinstance(getattr(self,n),subelement_wrapper):
                # Convert single element to a set of elements
                setattr(self,n,
                        subelement_set((getattr(self,n),obj)))
            else:
                assert False # can't happen 

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


class subelement_set(set):
    """A set of sub-elements."""
    pass

class subelement_wrapper(object):
    """Class to wrap a sub-Element's id and transform attrs."""
    def __init__(self,base,obj):
        self._base = base
        self._obj = obj

    def isinstance(self,cls):
        return self._obj.isinstance(cls)

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

    def __iter__(self):
        for v in self._obj:
            yield subelement_wrapper(self._base,v)

    def iterlayout(self,*args,**kwargs):
        for l in self._obj.iterlayout(*args,**kwargs):
            yield subelement_wrapper(self._base,l)

    def __getitem__(self,key):
        r = self._obj[key]
        return [subelement_wrapper(self._base,e) for e in r]

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
