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

from Tuke.context.wrapped_str_repr import unwrapped_repr
from collections import deque

def shortest_class_name(cls):
    """Returns the shortest class name for cls"""

    class_name = cls.__name__
    module_name = cls.__module__

    # Try to find a shorter representation of the module name.
    #
    # Often you'll get stuff like Tuke.element.Element, where the Tuke
    # __init__ code has a from element import Element line, find those
    # cases.
    t = module_name
    while True:
        t = t.split('.')[:-1]
        t = '.'.join(t)

        if not t:
            break


        # The from_list has to be set to something, or __import__ will only
        # return the top level module, IE, Tuke when asked for Tuke.geometry
        m = __import__(t,{},{},[class_name])

        try:
            if m.__dict__[class_name] is cls:
                module_name = t
                break
        except KeyError:
            continue

    return module_name + '.' + class_name 

def wrapped_repr_helper(fn):
    """Decorator to make writing __wrapped_repr__ functions easier."""

    def f(self):
        (args,kwargs) = fn(self)

        if not args:
            args = ()
        if not kwargs:
            kwargs = {}

        r = deque() 

        # str objects are special cased, and get str-ed, not repr-ed, so we
        # need to add quotes manually.
        def quote_str(obj):
            if obj.__class__ == str:
                return ("'",obj,"'")
            else:
                return (obj,)

        # positional arguments are easy, just insert a ',' between each one
        if args:
            for a in args:
                r.extend(quote_str(a))
                r.append(',')
            r.pop()

        # Keyword arguments get transformed into name=value syntax sorted by
        # name.
        if kwargs:
            if r:
                r.append(',')
            for n,v in sorted(kwargs.iteritems()):
                r.append(n)
                r.append('=')
                r.extend(quote_str(v))
                r.append(',')
            r.pop()

        r.appendleft('(')
        r.appendleft(shortest_class_name(self.__class__))
        r.append(')')
        return tuple(r) 

    return f

def repr_helper(fn):
    """Decorator to make writing __repr__ functions easier.

    Writing a __repr__ function designed to produce output that can be passed
    to eval() is relatively involved, with subtle issues like what is the full
    name of the class. This decorator allows the __repr__ function to simply
    return a (args,kwargs) tuple instead, the decorator will handle the rest.
    """
    fn = wrapped_repr_helper(fn)
    def f(self):
        # Isn't this a fun little bit of sticky glue?
        class shim:
            def __wrapped_repr__(shim_self):
                return fn(self)
        return unwrapped_repr(shim())

    return f

def non_evalable_repr_helper(fn):
    """Decorator for __repr__ functions that return non-eval()able strings.

    Lets you add informative keywords, turning:

    <Frob.foo instance at 0xb782bf2c>

    into:

    <Frob.foo instance at 0xb782bf2c, has_bar=True, frob_speed=100>

    To use simply have your __repr__ function return a dict of keys and values.

    Note that old-style classes are not supported.
    """

    def f(self):
        kw = fn(self)

        # Think, recursion...
        rpr = object.__repr__(self)

        if not kw:
            return rpr
        else:
            return rpr[:-1] + ', ' \
                   + ', '.join(['%s=%s' % (n,repr(v)) for n,v in sorted(kw.iteritems())]) \
                   + '>'
    return f
