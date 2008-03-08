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

class Id(object):
    """Element identifiers.
    
    Id's are identifiers with a path. The path is relative, so for instance
    ../Vcc means Vcc in our parent's context, similarly foo/Vcc means Vcc in
    foo, a sub-element.
    """

    __slots__ = ('id')

    def __init__(self,s = '.'):
        """Create a new Id from s

        s may be a string or another Id
        """

        if isinstance(s,Id):
            s = str(s)

        if not isinstance(s,str):
            raise TypeError, "%s is not an Id or a string: %s" % (type(s),s)

        self.id = s.split('/')

        self.normalize()

    def random(cls,bits = 64):
        """Create a random Id
        
        bits - bits of randomness
        """

        import random
        
        s = hex(random.randint(0,2 ** bits))[2:-1].zfill(bits / 4).lower()

        return cls(s) 
    random = classmethod(random)

    def normalize(self):
        id = []

        for i in self.id:
            if i == '..':
                if id and id[-1] != '..':
                    id.pop()
                else:
                    id.append(i)
            elif i in ('.',''):
                continue
            else:
                id.append(i)

        self.id = tuple(id)


    def __add__(self,b):
        n = Id()

        # Why the Id(b)? That's to allow b to be anything that's acceptable by
        # Id(), yet, if it isn't, to properly raise a TypeError
        n.id = self.id + Id(b).id

        n.normalize()

        return n 

    def __str__(self):
        if self.id:
            return reduce(lambda a,b: a + '/' + b,self.id)
        else:
            return '.'

    def __eq__(self,b):
        return str(self) == str(b)

    def __ne__(self,b):
        return not self.__eq__(b)

    def __len__(self):
        return len(self.id)

    def __cmp__(self,other):
        """Compare

        This is done in terms of higher or lower in the hierarchy, with equal
        hierarchies being compared alphabetically."""

        if len(self) == len(other):
            return cmp(self.id,other.id)
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
        e = self.id.__getitem__(s)

        # In the Id[0] case, e is bare, however the following code is assuming
        # that e is a tuple. Fix.
        if not isinstance(e,tuple):
            e = (e,)

        # Convert to an Id to return
        return Id('/'.join(e))

    def __hash__(self):
        return hash(self.id)

def rndId():
    """Alias for Id.random()"""
    return Id.random()
