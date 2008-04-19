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

import weakref

from Tuke import Element,Id

ElementRef_cache = weakref.WeakKeyDictionary()

class ElementRef(object):
    """Weakly reference an Element from a given context.

    Why from a given context? Well, the context is what determines what the
    referenced Element is. For instance, in the context of 'a', 'b' is a
    different thing if a.b is deleted and replaced. So an ElementRef only
    stores a reference to the Element providing the context, and the Id of the
    wrapped Element.

    """

    # See Connects code for all the gory details. In short, since there is one,
    # and only one, ElementRef object for each base/ref combo each explicit
    # connection maps to one ElementRef object. This key is then used to help
    # implement the *implicit* connectivity map.
    _implicit_connectivity_key = None

    base = None
    id = None

    def __new__(cls,base,ref):
        """Create a new ElementRef

        base - Context providing Element 
        ref - Referenced Element, or Id

        A subtle point is that for any given base/id only one
        ElementRef object will be created, subsequent calls will return
        the same object. 
        
        """

        id = None
        try:
            id = ref.id
        except AttributeError:
            id = Id(ref)

        try:
            return ElementRef_cache[base][id]
        except KeyError:
            self = object.__new__(cls)

            self.base = base
            self.id = id

            try: 
                ElementRef_cache[base][id] = self
            except KeyError:
                ElementRef_cache[base] =\
                        weakref.WeakValueDictionary()
                ElementRef_cache[base][id] = self

            return self

    def __call__(self):
        """Dereference

        self.base[self.id]

        """
        return self.base[self.id]
