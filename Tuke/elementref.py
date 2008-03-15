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
from Tuke import repr_helper

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

        object.__setattr__(self_real,'_ref_target_id',Tuke.Id(target_id))

        self('set_target')(target)

    def set_target(self,target):
        """Set target object."""
        from Tuke import ElementWrapper
        assert isinstance(target,(Tuke.Element,Tuke.ElementWrapper,type(None)))

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
