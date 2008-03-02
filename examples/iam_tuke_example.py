#!/usr/bin/python
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

"""Module to make life easier for Tuke examples"""

# hook in-tree tuke into python path if running example
import sys
import os.path
my_dir      = os.path.dirname(__file__)         # examples/
tuke_top   = os.path.split(my_dir)[0]          # ../
tuke_dir   = os.path.join(tuke_top, 'Tuke')  # ../Tuke/
if os.path.isdir(tuke_dir):
    sys.path.insert(0, tuke_top)
