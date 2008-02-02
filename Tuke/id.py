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

class Id(object):
    """Element Ids."""

    def __init__(self,s = '.'):
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
