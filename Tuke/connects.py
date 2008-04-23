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

"""Element connectivity.

Connectivity between elements refers to the connections between elements that
don't fall under the standard parent/child graph. This is used to store the
netlist information and to make traces possible.

Connectivity comes in two types, explicit and implicit. An explicit connection
is one that is stored in a Connects object in an Element. The implicit
connection is the reverse of that explicit connection. An explicit connection
may be left dangling if there is no actual Element at the location that it's
ElementRef is pointing to. Implicit connections simply don't exist until the
corresponding explicit connection is made.

Connectivity is stored per Element, but cached globally for speed and to allow
for implicit connections.

"""

import Tuke
import Tuke.context
import Tuke.repr_helper
import weakref

# Implicit connections are the most interesting feature to implement.  Elements
# are always relative. For example a Component might have an explicit
# connection to '../vcc' If that Component is moved from one parent to another,
# those explicit connections now map to different Elements. This means that the
# implicit connection cache has to get updated.  To deal with that, the parent
# change hooks are used so that changes to the Element graph can be detected
# and the associated implicit connections updated.
#
# The global connections cache is implemented as a WeakKeyDict of WeakKeyDicts,
# in the form:
#
# _implicitly_connected[a.connects][b.connects] = b
#
# Where a in an Element and b is a Element. The above would state that a is
# implicitly connected to b, and therefore b is the ElementRef who's
# dereferenced Element is *explicitly* connected to a. _i_c[a.c][b.c._i_c_k]
# evaluates to the actual Element that a is implicitly connected too.
#
# The key is the usage of WeakKeyDicts. Consider what happens if a goes away.
# It gets garbage collected, and suddenly that second level WeakKeyDict gets
# deleted as well, automaticly getting rid off all those implicit connections.
# If b is deleted, the result is similar.
_implicitly_connected = weakref.WeakKeyDictionary()

class Connects(set):
    """Per-Element connectivity info.
   
    The Set of Elements an Element is connected too. The elements in the set
    are stored as ElementRefs, and may or may not be resolvable to actual
    elements.

    Utility functions are provided to access the global information on
    connected elements, such as finding the set of all Elements that an Element
    is connected too.
    """

    def __new__(cls,iterable = (),base = None):
        """Create connectivity info

        iterable - Optional iterable of Ids to add.
        base - Base element, may be set after initialization
        """
        self = set.__new__(cls) 

        assert isinstance(base,(Tuke.Element,type(None)))

        _implicitly_connected[self] = weakref.WeakKeyDictionary() 

        for i in iterable:
            super(cls,self).add(i)

        if base is not None:
            self.base = base
        return self


    def add(self,ref):
        """Add an explicit connection.

        ref - Element or Id
        """

        ref = self._make_ref(ref)
        super(self.__class__,self).add(ref)

        self._set_implicit_connectivity(ref)

    def to(self,other):
        """True if self is connected to other, explicity or implicitly."""

        ref = self._make_ref(other)

        if ref in self:
            return True
        else:
            try:
                return _implicitly_connected[ref.connects][self]
            except (Tuke.ElementRefError, KeyError):
                return False

    def __contains__(self,other):
        """True if there is an explicit connection from self to other"""
        ref = self._make_ref(other)
        return super(self.__class__,self).__contains__(ref)


    # Private stuff below:

    def __hash__(self):
        # Sets, which we are a subclass of, are not hashable, however we depend
        # on using Connects objects as keys in WeakKeyDicts.
        return id(self)

    def _set_implicit_connectivity(self,ref):
        """Set implicit connectivity between self and what ref points to."""
        if ref._base is not None:

            change_report_stack = None
            try:
                _implicitly_connected[self][ref.connects] = True
                change_report_stack = ref._get_ref_stack()
            except Tuke.ElementRefError,err:
                # Looks like ref isn't fully accessible, however, we should
                # still use the partially dereferenced stack to figure out what
                # parent changes we should trigger a reset of connectivity on,
                # as any of them could have their parent set, and then have
                # connectivity restored.
                change_report_stack = err.partial_stack


        # The implicit_reference_updater object gets put into many Elements
        # callback list, but only gets called by one Element. The key, no pun
        # intended, is that the callbacks are WeakKeyDicts, and by removing the
        # one reference to the object in ref, the garbage collector will take
        # care of the rest.
        class implicit_reference_updater(object):
            def __init__(self,connects,ref):
                self.connects = connects
                self.ref = ref
                self.enabled = True
            def __call__(self,*args,**kwargs):
                if self.enabled: # in case that gc isn't fast enough
                    self.enabled = False
                    self.connects._set_implicit_connectivity(self.ref)
        ref._implicit_connectivity_key = implicit_reference_updater(self,ref)
        for e in change_report_stack:
            Tuke.context.source.notify(e,e.parent,
                    ref._implicit_connectivity_key,ref._implicit_connectivity_key)

    def _make_ref(self,ref):
        # This is actually kinda clever. We're storing ElementRefs, and one
        # ElementRef is another ElementRef if their base and reference are
        # equal... So, test for that, and simply return the ref!
        try:
            if not (ref._base == self._base):
                raise ValueError, \
                    "Base Elements must match, got %s, need %s" % \
                            (ref._base,self._base)

            return ref
        except AttributeError:
            try:
                return Tuke.ElementRef(self._base,Tuke.Id(ref))
            except TypeError:
                raise TypeError, "Expected an Id, string, or ElementRef, not %s" % type(ref)
        

    def _get_base(self):
        return self._base
    def _set_base(self,v):
        self._base = v
        old = tuple(self)
        self.clear()
        for e in old:
            self.add(e)
    base = property(_get_base,_set_base)

    @Tuke.repr_helper.repr_helper
    def __repr__(self):
        ids = tuple([r.id for r in self])
        return ((sorted(ids),),
                {})
