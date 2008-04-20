# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
# (c) 2008 Peter Todd <pete@petertodd.org>
#
# This program is made available under the GNU GPL version 3.0 or
# greater. See the accompanying file COPYING for details.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.

from __future__ import with_statement

from unittest import TestCase

from Tuke import Id

from Tuke.context.wrapped_str_repr import unwrapped_str,unwrapped_repr

bypass = None
class wrapped_str_reprTest(TestCase):
    def test_Source(self):
        global bypass
        class skit:
            def __wrapped_repr__(self):
                return bypass
            __repr__ = unwrapped_repr
            def __wrapped_str__(self):
                return bypass
            __str__ = unwrapped_str

        a = skit()

        def T(chunks,expectedr,expecteds = None):
            global bypass
            bypass = chunks
            if expecteds is None:
                expecteds = expectedr
            gotr = repr(a)
            gots = str(a)
            self.assert_(expectedr == gotr,
                    'got repr: %s  expected: %s' % (gotr,expectedr))
            self.assert_(expecteds == gots,
                    'got str: %s  expected: %s' % (gots,expecteds))

        T((),'')
        T((None,),'None')
        T((1506,' nix',' nix'),"1506 nix nix")
        T((Id('.'),),repr(Id('.')),'.')
        T((Id('a'),),repr(Id('a')),'a')

        class foo:
            def __wrapped_repr__(self):
                return (Id('foo'),)
            def __wrapped_str__(self):
                return (Id('foo'),)
            __repr__ = unwrapped_repr
            __str__ = unwrapped_str

        class bar:
            def __wrapped_repr__(self):
                return (Id('bar'),',',foo())
            def __wrapped_str__(self):
                return (Id('bar'),',',foo())
            __repr__ = unwrapped_repr
            __str__ = unwrapped_str

        class far:
            def __wrapped_repr__(self):
                return (Id('far'),',',bar())
            def __wrapped_str__(self):
                return (Id('far'),',',bar())
            __repr__ = unwrapped_repr
            __str__ = unwrapped_str


        T((far(),),
                "Tuke.Id('far'),Tuke.Id('bar'),Tuke.Id('foo')",
                "far,bar,foo")
