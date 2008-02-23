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
from Tuke import Id


class Element(object):
    """Base element class."""

    # XML attributes, and there default values.
    #
    # This should include all state that needs to be saved in the long term.
    # All values in this list should be eval(repr()) safe.
    saved_state = ('id',)

    def extra_saved_state(self):
        """For extra saved state that must be auto-generated in some way."""
        return ()

    def __init__(self,id=Id()):
        self.id = id

        self.subs = []

    def __iter__(self):
        for i in self.subs:
            yield i

    def add(self,b):
        self.subs.append(b)

    def _save(self,doc,subs):
        """Actual save function, seperated out for Translate-type subclassing."""

        r = doc.createElement(self.__module__ + '.' + self.__class__.__name__)

        # Save state.
        state = None
        try:
            state = self.__getstate__()
        except AttributeError:
            state = self.__dict__

        for n,v in state.iteritems():
            # subs is handled below, so ignore it if appropriate.
            #
            # Note that this means that a custom __savestate__ function can't
            # return a dict with 'subs' in it...
            if n == 'subs':
                continue 

            r.setAttribute(n,repr(v))

        for s in subs:
            r.appendChild(s.save(doc))

        return r

    def save(self,doc):
        """Returns an XML minidom object representing the Element"""
        return self._save(doc,getattr(self,'subs',[]))

    def render(self):
        geo = []

        for s in self.subs:
            for i,l,s in s.render():
                geo += [(self.id + i,l,s)]

        return geo

def load_Element(dom):
    """Loads elements from a saved minidom"""

    # Since the xml is saved as a tree, and elements depend on their
    # subelements, the load operation must be done in a depth-first recursive
    # manner.

    subs = []
    for sub in dom.childNodes:
        subs.append(load_Element(sub))

    
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
        self.id = id
