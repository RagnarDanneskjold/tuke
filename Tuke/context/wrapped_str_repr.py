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

"""Utility functions for objects using the __wrapped_(str|repr)__ protocol."""

# It's instructive to note that these 13 lines of Python code duplicate the
# functionality of 124 lines of C in wrapper.c
def unwrapped_str(self):
    """__str__ replacement for objects implementing __wrapper_str__"""
    return ''.join(map(str,
                        self.__wrapped_str__()))

def unwrapped_repr(self):
    """__repr__ replacement for objects implementing __wrapper_repr__"""
    def f(o):
        if o.__class__ == str:
            return str(o)
        else:
            return repr(o)
    return ''.join(map(f,
                        self.__wrapped_repr__()))
