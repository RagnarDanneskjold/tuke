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

"""Context managment."""

import weakref

class context_source(object):
    """Defines a source of context information."""
    def __init__(self,initial):
        """Define context source, with an initial value"""
        self.initial = initial
        self.byobj = weakref.WeakKeyDictionary()

    def __get__(self,obj,objtype):
        if obj is None:
            return self.initial
        else:
            try:
                return self.byobj[obj]
            except KeyError:
                self.byobj[obj] = self.initial
                return self.initial

        return None
    def __set__(self,obj,v):
        self.byobj[obj] = v
