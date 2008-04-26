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

"""

from __future__ import with_statement

import Tuke
import Tuke.context
import Tuke.context.wrapped_str_repr
import Tuke.repr_helper
import weakref

from Tuke.context.wrapper import unwrap

def _make_ref(base,ref):
    """Given an Id, or Element, return an Id

    base - Base Element

    If ref is an Element, makes sure that base and ref share a parent.

    """
    try:
        if not base.have_common_parent(ref):
            raise ValueError(
                    "No common parents, Element is on a different tree.")
        ref = ref.id
    except AttributeError:
        if not isinstance(ref,Tuke.Id):
            raise TypeError(
                "Expected an Id, Element, not %s" % type(ref))
    return ref


# Explicit connectivity is pretty easy to store, the Connects class is simply a
# set subclass and each explicit connection is simply stored essentially as an
# Id.
#
# Implicit connectivity is harder. Firstly implicit connectivity can change due
# to topology changes, either making, or in the future when Element.remove() is
# supported, breaking implicit connections. Secondly while the implicit
# connectivity info must be stored in the Elements that are being implicitly
# connected to for speed, if the Element.connects creating that connection is
# deleted, that info must automatically be removed. This is also tricky, as we
# can't use any __dealloc__ hooks.
#
# The solution here uses the Element.notify() mechanism heavilly, setting up
# callbacks along every Element in the explicit connection chain. The
# _elemref class then acts to maintain and process those callbacks. Connects
# is then a set of _elemrefs. At any point the whole shebang can be deleted,
# and the weakref callback mechanism used in notify will clean up everything.

class _elemref:
    """Connects explicit connection.

    Holds both the Id reference, and maintains/creates the implicit connection.

    """

    def __init__(self,connects,ref):
        self.ref = ref 

        self.connects = connects
        self._compute_implicit_callbacks()

    def _make_invalidator_callback(self):
        """Make an invalidator callback callable object.

        Each _elemref has a single invalidator callback associated with it,
        which, when called, triggers a re-compute of the implicit callbacks.
        This function simply makes a new one.
        """
        def invalidator(ref):
            self._compute_implicit_callbacks()
        return invalidator

    def _compute_implicit_callbacks(self):
        """Recompute the implicit callbacks chain.

        Starts fresh. The design here is to simply start fresh after each
        topology change. Given that most connects are going to be one or two
        levels deep, this is simpler, and probably more efficient, than a more
        complex "find what level changed" algorithm.

        """
        class Invalidator:
            def __init__(self,ref):
                self.ref = weakref.ref(ref)
                self.valid = True
            def __call__(self):
                if self.valid:
                    # One shot
                    self.valid = False

                    # Should only work if the original _elemref is alive.
                    ref = self.ref()
                    if ref is not None:
                        ref._compute_implicit_callbacks()

        # Old invalidator is deleted, garbage collection will take care of the
        # rest.
        self._invalidator_callable = Invalidator(self)

        # Walk from our parent element, to the destination, setting callbacks
        # along the way. While we're at it, the reverse path is being
        # calculated in p, for insertion into the target's implicitly connected
        # dict.
        e = unwrap(self.connects._parent)
        p = Tuke.Id('.')
        for i in tuple(tuple.__iter__(self.ref)) + (None,):
            if i is not None:
                e.notify(Tuke.Id(i),self._invalidator_callable)

                if i == '..':
                    p = e._id_real + p
                else:
                    p = Tuke.Id('..') + p
            try:
                e = unwrap(e[Tuke.Id(i)])
            except KeyError:
                # Didn't reach the last Element referenced in the path;
                # implicit connection doesn't exist because explicit connection
                # is dangling.
                break
            except TypeError:
                # Did reach the last Element referenced in the path. The
                # calculated reverse path is inserted as the key in
                # _implicitly_connected, the invalidator_callable is used as a
                # magic cookie. This is a WeakValueDict, so when the cookie
                # goes away, the entry does too.
                #
                # Note that gc-lag could turn this simple construct into a
                # problem when Element.remove is implemented.
                e.connects._implicitly_connected[p] = self._invalidator_callable
                break



class Connects(dict):
    """Per-Element connectivity info.
   
    The set of Elements an Element is connected too. Stored as a collection of
    bare Id's, which the parent element can evaluate to find the actual
    referring Element.

    """

    def __new__(cls,iterable = (),parent = None):
        """Create connectivity info

        iterable - Optional iterable of Ids to add.
        parent - Parent element, may be set after initialization
        """
        self = dict.__new__(cls) 

        assert isinstance(parent,(Tuke.Element,type(None)))

        self._implicitly_connected = weakref.WeakValueDictionary()

        for i in iterable:
            self[i] = None 

        self._parent = parent
        return self

    def __init__(self,*args,**kwargs):
        # dict also has a __init__, ignore it
        pass

    def add(self,ref):
        """Add an explicit connection."""
        ref = _make_ref(self._parent,ref)
        eref = _elemref(self,ref)
        self[ref] = eref

    def to(self,ref):
        """True if self is connected to other, explicity or implicitly."""
        ref = _make_ref(self._parent,ref)

        if ref in self:
            return True
        else:
            if ref in self._implicitly_connected:
                return True
            else:
                return False

    def __contains__(self,ref):
        """True if there is an explicit connection from self to other"""
        ref = _make_ref(self._parent,ref)
        return super(self.__class__,self).__contains__(ref)


    # Private stuff below:

    def __hash__(self):
        # Sets, which we are a subclass of, are not hashable, however we depend
        # on using Connects objects as keys in WeakKeyDicts. For those purposes
        # treating the Connect as a magic cookie is fine.
        return id(self)


    def _get_parent(self):
        return self._parent
    def _set_parent(self,v):
        self._parent = v
        old = tuple(self)
        self.clear()
        for e in old:
            self.add(e)
    parent = property(_get_parent,_set_parent)

    @Tuke.repr_helper.wrapped_repr_helper
    def __wrapped_repr__(self):
        ids = self.keys() 
        return ((sorted(ids),),
                {})
    __repr__ = Tuke.context.wrapped_str_repr.unwrapped_repr
