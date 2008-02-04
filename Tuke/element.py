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

from Tuke import Id


class Element(object):
    """Base element class."""

    # Full name of the class for saving state.
    full_class_name = 'Tuke.Element'

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

        r = doc.createElement(self.full_class_name)

        # Save state.
        state = [(n,getattr(self,n)) for n in self.saved_state]
        state += self.extra_saved_state()
        for n,v in state:
            r.setAttribute(n,repr(v))

        for s in subs:
            r.appendChild(s.save(doc))

        return r

    def save(self,doc):
        """Returns an xml minidom object representing the Element"""
        return self._save(doc,getattr(self,'subs',[]))

    def render(self):
        geo = []

        for s in self.subs:
            for i,l,s in s.render():
                geo += [(self.id + i,l,s)]

        return geo

class SingleElement(Element):
    """Base class for elements without subelements."""
    __iter__ = None
    add = None
    def __init__(self,id=Id()):
        self.id = id
