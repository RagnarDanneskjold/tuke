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

context_source_callbacks_by_obj = weakref.WeakKeyDictionary() 

class _empty(object):
    pass
_initial_key = _empty()
class context_source(object):
    """Define a source of context information.
    
    A source of context is simply an object attribute whose value, if changed,
    would change the context of another object. A simple example is the
    transform attribute of Elements, which if changed changes context-dependent
    geometry of sub-Elements.

    To trap changes to the attribute context_source is implemented with the
    descriptor protocol, and us used much like property::

        class Element(object):
            transform = context_source(Transformation())

    Any instance of Element now has a .transform attribute who's initial value
    is Transformation(), and can be gotten and set like any normal attribute.
    Just like normal class attributes, non-immutable attributes are shared
    accross all class instances. Therefor all context_source types should be
    immutable.

    Element.transform also is equal to Transformation(), unlike property where
    class.some_property is visible as a property method object. This is done so
    introspective code can determine what a classes attributes initial values
    are without having to know about context_sources.

    Note that due to implementation reasons context_source attribute values and
    context_source attribute containing classes must be weakref-able.

    """

    def __init__(self,initial):
        """Define context source, with an initial value"""
        self.byobj = weakref.WeakKeyDictionary()
        self.byobj[_initial_key] = initial

    def __get__(self,obj,objtype):
        if obj is None:
            return self.byobj[_initial_key] 
        else:
            try:
                return self.byobj[obj]
            except KeyError:
                self.byobj[obj] = self.byobj[_initial_key] 
                return self.byobj[obj] 

        return None
    def __set__(self,obj,v):
        # Get the list of callbacks corresponding to the current value first,
        # before we wipe out that value.
        attrs_of_obj = None
        old_callbacks = {}
        try:
            attrs_of_obj = context_source_callbacks_by_obj[obj]
        except KeyError:
            context_source_callbacks_by_obj[obj] = {}
            attrs_of_obj = context_source_callbacks_by_obj[obj]
        else:
            try:
                old_callbacks = attrs_of_obj[self.byobj[obj]]

                # Without this del every time a context_source attribute was
                # set to a different value, it'd leak a bit of memory by
                # leaving a reference to the value in attrs_of_obj[value]
                del attrs_of_obj[self.byobj[obj]]
            except KeyError:
                pass

        self.byobj[obj] = v

        attrs_of_obj[v] = weakref.WeakKeyDictionary()

        # Clean slate, callbacks can safely call notify()
        for o,fn in old_callbacks.iteritems():
            fn(o)


def notify(obj,attr,callback_obj,callback):
    """Set a callback for any change of a context_source

    - `obj`: the object containing the attribute.
    - `attr`: the attribute itself. 
    - `callback_obj`: passed to the callback.
    - `callback`: callback function in the form fn(callback_obj)

    A weakref is created to callback_obj, if this object is deleted, the
    callback is automatically removed as well. The callback function is called
    after the change to attr is recorded; the function may call notify() again
    to re-register.

    Due to the implementation, if attr is not a context_source, an error will
    *not* be raised.

    """

    # For the terminally curious... The reason why specifying attr isn't enough
    # is that by the time attr gets passed to notify() it already *is* the
    # attribute; __get__ returns the attribute itself. So we need to know the
    # object containing attr to be able to fully know exactly when to notify,
    # important when multiple objects reference the same attribute, such as in
    # Element.parent
    #
    # The reason why checking that attr is actually a context_source is
    # similar, attr itself does not give that information, and looking for attr
    # in obj.__dict__ doesn't work as well, as even .__dict__ lookups still
    # trigger the descriptor protocol and give us attr. Secondly
    # context_sources are defined at the class level and have no mechanism for
    # determining that an instance of a class has been defined. So we can't go
    # looking for attr in the context_source_callbacks_by_obj[obj] dict,
    # because even if it's valid it might not be in there yet if no call backs
    # have been set.


    attrs_of_obj = None
    try:
        attrs_of_obj = context_source_callbacks_by_obj[obj]
    except KeyError:
        context_source_callbacks_by_obj[obj] = {}
        attrs_of_obj = context_source_callbacks_by_obj[obj]
    
    cb = None
    try:
        cb = attrs_of_obj[attr]
    except KeyError:
        cb = weakref.WeakKeyDictionary()
        attrs_of_obj[attr] = cb 

    cb[callback_obj] = callback
