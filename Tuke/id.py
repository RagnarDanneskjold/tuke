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

from Tuke.uuid import uuid4

class Id(object):
    """Element identifiers.
    
    Id's are identifiers with a path. The path is relative, so for instance
    ../Vcc means Vcc in our parent's context, similarly foo/Vcc means Vcc in
    foo, a sub-element.
    """

    __slots__ = ('id')

    def __init__(self,s = '.'):
        if isinstance(s,Id):
            s = str(s)
        self.id = s.split('/')

        self.normalize()

    def normalize(self):
        id = []

        prev = None
        for i in self.id:
            if i == '..' and prev not in ('..',None):
                id.pop()
            elif i in ('.',''):
                continue # to avoid setting prev
            else:
                id.append(i)

            prev = i

        if not id:
            id = ['.']

        self.id = tuple(id)


    def __add__(self,b):
        n = Id()

        n.id = self.id + b.id

        n.normalize()

        return n 

    def __str__(self):
        if self.id:
            return reduce(lambda a,b: a + '/' + b,self.id)
        else:
            return ''

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

    def __repr__(self):
        s = str(self)

        return 'Id(\'%s\')' % s

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
    """Returns a randomized element Id

    Internally simply generates a UUID to insure uniqueness."""

    return Id(str(uuid4()))
