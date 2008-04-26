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

import Tuke.context as context
import Tuke.repr_helper

import re

valid_id_re = re.compile('^([_A-Za-z][_A-Za-z0-9]*|\.|\.\.)$')

def normalize(self):
    r = []

    for i in self:
        if i == '..':
            if r and r[-1] != '..':
                r.pop()
            else:
                r.append(i)
        elif i in ('.',''):
            continue
        else:
            r.append(i)

    return r

class Id(tuple,context.wrapper.Translatable):
    """Element identifiers.
    
    Id's are identifiers with a path. The path is relative, so for instance
    ../Vcc means Vcc in our parent's context, similarly foo/Vcc means Vcc in
    foo, a sub-element.
    """

    def __new__(cls,s = ''):
        """Create a new Id from s

        s may be a string or another Id
        """

        if isinstance(s,Id):
            # Skip normalization if possible.
            if cls is Id:
                return s
            else:
                # So Id subclasses work
                return tuple.__new__(cls,tuple.__iter__(s))

        try:
            id = s.split('/')
        except AttributeError:
            raise TypeError, "%s is not an Id or a string: %s" % (type(s),s)

        id = normalize(id)

        # Has to be last, as '/'.split('/') == ('','')
        for p in id:
            if not valid_id_re.match(p):
                raise ValueError, "'%s' is not a valid Id" % s

        return tuple.__new__(cls,id)

    @classmethod
    def random(cls,bits = 64):
        """Create a random Id
        
        bits - bits of randomness
        """

        import random
        
        s = '_' + hex(random.randint(0,2 ** bits))[2:-1].zfill(bits / 4).lower()

        return tuple.__new__(cls,(s,)) 


    def relto(self,base):
        """Returns self relative to base.

        By that we mean assuming self and base are starting from the same point
        in the tree, from the perspective of base, where is self?

        Id('a').relto('a') == '.'
        Id('a').relto('b') == '../b'
        Id('a/b/c').relto('a') == 'b/c'
        Id('../b/c').relto('a') == '../../b/c'
        """
        # Discard common prefixes
        i = 0
        while i < len(self) and i < len(base) and self[i] == base[i]:
            i += 1

        # Whatever is left in base must be turned into ../'s
        r = Id('../' * (len(base) - i))

        # And add on the uncommon part of what we're looking for
        return r + self[i:]
        

    def __add__(self,b):
        if not b:
            return self
        n = normalize(tuple.__add__(self,b))

        return tuple.__new__(Id,n) 

    def __str__(self):
        if self:
            return '/'.join(tuple.__iter__(self))
        else:
            return '.'

    def __eq__(self,b):
        return tuple.__eq__(self,b)

    def __ne__(self,b):
        return not self.__eq__(b)

    def __gt__(self,other):
        if len(self) == len(other):
            return tuple.__gt__(self,other)
        elif len(self) > len(other):
            return True
        else:
            return False

    def __lt__(self,other):
        if len(self) == len(other):
            return tuple.__lt__(self,other)
        elif len(self) < len(other):
            return True
        else:
            return False

    def __ge__(self,other):
        if len(self) == len(other):
            return tuple.__gt__(self,other)
        elif len(self) > len(other):
            return True
        else:
            return False

    def __le__(self,other):
        if len(self) == len(other):
            return tuple.__lt__(self,other)
        elif len(self) < len(other):
            return True
        else:
            return False

    def __getslice__(self,l,u):
        return tuple.__new__(Id,
                             tuple.__getslice__(self,l,u))

    def __getitem__(self,i):
        r = tuple.__getitem__(self,i)
        if isinstance(r,str):
            r = (r,)
        return tuple.__new__(Id,r)

    def __iter__(self):
        for i in tuple.__iter__(self):
            yield tuple.__new__(Id,(i,))

    def _build_context(self,base,reverse):
        assert len(self) == 1
        if reverse:
            return base + Id('..')
        else:
            return base + self

    def _apply_context(self,elem):
        return elem.id + self

    def _remove_context(self,elem):
        return self.relto(elem.id)

    @Tuke.repr_helper.repr_helper
    def __repr__(self):
        s = str(self)

        return ((s,),None) 

def rndId():
    """Alias for Id.random()"""
    return Id.random()
