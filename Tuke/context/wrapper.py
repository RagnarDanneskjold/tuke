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

import Tuke

# cancel the cache, lets get making a new class every time working first

# need two levels of derived classes, one for most of the wrapping, and the
# other to trap setattr calls

# Cache of pre-wrapped classes
prewrapped = {}

def wrap(obj,context):
    """Wrap an object in a context.

    The wrapping translates all data going in and coming out of the wrapped
    object. Data coming from the object is wrapped in the context, data going
    into the object has the context removed.

    To achieve reasonable performance the wrapper is implemented, not by the
    usual __getattribute__ style tricks, but rather by dynamically creating a
    new subclass of the wrapped objects class, with all methods wrapped and
    attributes replaced by property attributes.

    FIXME: write bit about __class__ limitations and what not
    """

    assert isinstance(context,Tuke.Element)

    wrapped_class = None
    try:
        wrapped_class = prewrapped[obj.__class__]
    except KeyError:
        wrapped_dict = {}

        for n in obj.__class__.__dict__.keys():

            # Right here is the guts of the magic. We're going through the
            # wrapped class's dict. For *every* name in it, construct a special
            # property attribute that gets/sets the value for that attribute
            # name. This new property attribute wraps accesses to the
            # underlying attribute and does the automatic conversion to and
            # from the wrapping context.
            #
            # That names like __doc__ get wrapped too is unimportant, their
            # underlying value is get or set with a very minor performance
            # penalty. Stuff like __iter__ and __getitem__ actually *has* to
            # have it's output wrapped.
            #
            # __setattr__ is an interesting case, which is explained later.

            def mkgetx(name):
                n = name
                def getx(self):
                    print 'getx',n
                    r = getattr(self._wrapped_obj,n)
                    try:
                        ac = r._apply_context
                    except AttributeError:
                        return r
                    else:
                        return ac(self._wrapping_context)
                return getx

            def mksetx(name):
                n = name
                def setx(self,value):
                    print 'setx',n,value
                    try:
                        ac = value._remove_context
                    except AttributeError:
                        pass
                    else:
                        value = value._remove_context(self._wrapping_context)
                    setattr(obj,n,value)
                return setx

            wrapped_dict[n] = property(mkgetx(n),mksetx(n))

        def __new__(cls,obj,context):
            r = object.__new__(cls)
            r._wrapped_obj = obj
            r._wrapping_context = context
            return r

        def __init__(self,obj,context):
            pass

        def __setattr__(self,n,v):
            # Element adding stuff to it... need to think this through.

            # Still should be safe to modify class directly, it's quite ok if
            # we keep filling up the class with stuff, all classes are the
            # same, so long as there is a way to remove the entries if no class
            # uses them anymore.
            pass

        wrapped_dict['__new__'] = __new__
        wrapped_dict['__init__'] = __init__

        wrapped_class = type('wrapped_' + obj.__class__.__name__,
                             (obj.__class__,),wrapped_dict)

        prewrapped[obj.__class__] = wrapped_class

    r = wrapped_class(obj,context)

    return r
