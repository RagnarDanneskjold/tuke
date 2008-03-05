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

def repr_helper(fn):
    """Decorator to make writin __repr__ functions easier.

    Writing a __repr__ function designed to produce output that can be passed
    to eval() is relatively involved, with subtle issues like what is the full
    name of the class. This decorator allows the __repr__ function to simply
    return a (args,kwargs) tuple instead, the decorator will handle the rest.

    As a special case, if the repr function needs to change the class name, set
    '_repr_helper_class_name_override' This is useful if there are alternate,
    more legible, ways of creating the object.
    """

    def f(self):
        (args,kwargs) = fn(self)

        if not args:
            args = ()
        if not kwargs:
            kwargs = {}

        class_name = None
        try:
            class_name = kwargs['_repr_helper_class_name_override']
            del kwargs['_repr_helper_class_name_override']
        except:
            class_name = self.__class__.__name__

        # positional arguments are easy, just repr each one
        args = [repr(a) for a in args] 

        # keyword arguments get transformed into name = value syntax
        kwargs = ['%s = %s' % (n,repr(v)) for (n,v) in kwargs.iteritems()]

        args_str = ','.join(args + kwargs)

        return '%s.%s(%s)' % (self.__class__.__module__,class_name,
                              args_str)

    return f

def non_evalable_repr_helper(fn):
    """Decorator for __repr__ functions that return non-eval()able strings.

    Lets you add informative keywords, turning:

    <Frob.foo instance at 0xb782bf2c>

    into:

    <Frob.foo instance at 0xb782bf2c, has_bar=True, frob_speed=100>

    To use simply have your __repr__ function return a dict of keys and values.
    """

    def f(self):
        kw = fn(self)

        # Think, recursion...
        rpr = super(self.__class__,self).__repr__()

        if not kw:
            return rpr
        else:
            return rpr[:-1] + ', ' \
                   + ', '.join(['%s=%s' % (n,repr(v)) for n,v in kw.iteritems()]) \
                   + '>'
    return f
