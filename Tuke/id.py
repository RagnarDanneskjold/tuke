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

from Tuke import repr_helper

import re

valid_id_re = re.compile('^([_A-Za-z][_A-Za-z0-9]*|\.|\.\.)$')

class Id(object):
    """Element identifiers.
    
    Id's are identifiers with a path. The path is relative, so for instance
    ../Vcc means Vcc in our parent's context, similarly foo/Vcc means Vcc in
    foo, a sub-element.
    """

    __slots__ = ('_id')

    def __init__(self,s = ''):
        """Create a new Id from s

        s may be a string or another Id
        """

        if isinstance(s,Id):
            s = str(s)

        if not isinstance(s,str):
            raise TypeError, "%s is not an Id or a string: %s" % (type(s),s)

        self._id = s.split('/')

        self.normalize()

        # Has to be last, as '/'.split('/') == ('','')
        for p in self._id:
            if not valid_id_re.match(p):
                raise ValueError, "'%s' is not a valid Id" % s

    @classmethod
    def random(cls,bits = 64):
        """Create a random Id
        
        bits - bits of randomness
        """

        import random
        
        s = '_' + hex(random.randint(0,2 ** bits))[2:-1].zfill(bits / 4).lower()

        return cls(s)

    def normalize(self):
        _id = []

        for i in self._id:
            if i == '..':
                if _id and _id[-1] != '..':
                    _id.pop()
                else:
                    _id.append(i)
            elif i in ('.',''):
                continue
            else:
                _id.append(i)

        self._id = tuple(_id)

    def relto(self,base):
        """Returns self relative to base.

        By that we mean assuming self and base are starting from the same point
        in the tree, from the perspective of base, where is self?

        Id('a').relto('a') == '.'
        Id('a').relto('b') == '../b'
        Id('a/b/c').relto('a') == 'b/c'
        Id('../b/c').relto('a') == '../../b/c'
        """
        base = Id(base)

        # Discard common prefixes
        i = 0
        while i < len(self) and i < len(base) and self[i] == base[i]:
            i += 1

        # Whatever is left in base must be turned into ../'s
        r = Id('../' * (len(base) - i))

        # And add on the uncommon part of what we're looking for
        return r + self[i:]
        

    def __add__(self,b):
        n = Id()

        # Why the Id(b)? That's to allow b to be anything that's acceptable by
        # Id(), yet, if it isn't, to properly raise a TypeError
        n._id = self._id + Id(b)._id

        n.normalize()

        return n 

    def __str__(self):
        if self._id:
            return reduce(lambda a,b: a + '/' + b,self._id)
        else:
            return '.'

    def __eq__(self,b):
        b = Id(b)
        return self._id == b._id

    def __ne__(self,b):
        return not self.__eq__(b)

    def __len__(self):
        return len(self._id)

    def __cmp__(self,other):
        """Compare

        This is done in terms of higher or lower in the hierarchy, with equal
        hierarchies being compared alphabetically."""

        if len(self) == len(other):
            return cmp(self._id,other._id)
        else:
            if len(self) < len(other):
                return -1
            else:
                return 1

    @repr_helper
    def __repr__(self):
        s = str(self)

        return ((s,),None) 

    def __getitem__(self,s):
        e = self._id.__getitem__(s)

        # In the Id[0] case, e is bare, however the following code is assuming
        # that e is a tuple. Fix.
        if not isinstance(e,tuple):
            e = (e,)

        # Convert to an Id to return
        return Id('/'.join(e))

    def __hash__(self):
        return hash(self._id)

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

def rndId():
    """Alias for Id.random()"""
    return Id.random()
