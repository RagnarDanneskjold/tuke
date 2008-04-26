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

import Tuke.repr_helper
import weakref
import Tuke.context.wrapped_str_repr
from Tuke.context.wrapper import wrap

from Tuke import Element,Id

class ElementRef(Id):
    """Weakly reference an Element from a given context.

    Essentially just a glorified Id, but also with some housekeeping. Namely
    the base.connects is updated and you can call the ElementRef to obtain the
    underlying Element.

    """

    def __new__(cls,*args):
        """Create a new ElementRef

        ref - Referenced Element, or Id
        base - Context providing Element

        """

        ref = None
        base = None
        if len(args) == 1:
            ref = args[0]
        elif len(args) == 2:
            base = args[0]
            ref = args[1]
        else:
            raise TypeError("%s.__new__() takes either 1 or 2 arguments, %d given",
                    cls.__name__,
                    len(args))

        try:
            ref = ref.id
        except AttributeError:
            if not isinstance(ref,Id):
                raise TypeError("Expected Element, ElementRef or Id, not %s" %
                                type(id))

        # Id.__new__(Id('foo')) short-circuits to directly return Id('foo'),
        # have to kludge around that.
        self = Id.__new__(cls,ref)

        self.base = base
        if self.base is not None:
            self.base.connects.add(self)

        return self

    def __call__(self):
        """Dereference

        self.base[self.id]

        """
        return self.base[self]

    def _apply_context(self,elem):
        r = elem.id + self
        r = ElementRef(r)
        r.base = wrap(self.base,elem,1)
        return r

    def _remove_context(self,elem):
        r = self.relto(elem.id)
        r = ElementRef(r)
        r.base = wrap(self.base,elem,0)
        return r

    @Tuke.repr_helper.wrapped_repr_helper
    def __wrapped_repr__(self):
        id = Id(self)
        return ((id,),{})
    __repr__ = Tuke.context.wrapped_str_repr.unwrapped_repr
