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

"""Conversion constants.

Usage:

Converting from inches to meters:

x = 10 * IN

Converting to inches from meters:

y = x / IN
"""

# Meters are the native unit
M = 1

# Other metric units
CM = M * 1e-2
MM = CM * 1e-1

# Imperial
IN = 25.4 * MM

# These two are used by geda, mils and mili-mils
MIL = IN * 1e-3
MMIL = MIL * 1e-3
