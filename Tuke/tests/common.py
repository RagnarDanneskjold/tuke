# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
# (c) 2007,2008 Peter Todd <pete@petertodd.org>
#
# This program is made available under the GNU GPL version 3.0 or
# greater. See the accompanying file COPYING for details.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.

"""Some stuff common to all tests"""

import shutil
import tempfile
import os

tmpd = ""

def dataset_path(name):
    """Given a dataset name returns the datasets path."""
    from os.path import join, split
    path = join(split(__file__)[0], 'data', name)

    assert(os.path.exists(path))

    return path

def clean_tmpd():
    """Sets tmpd to a unique name guaranteed to have nothing at it."""
    global tmpd
    if not tmpd or not os.path.exists(tmpd):
        tmpd = tempfile.mkdtemp(prefix="tuke_tests_")
    shutil.rmtree(tmpd)

def load_dataset(name):
    """Copy a dataset into the temp directory."""

    global tmpd
    clean_tmpd()

    shutil.copytree(dataset_path(name),tmpd)

def repr_file(path):
    """Returns a tuple fully representing a file."""

    
    symlink = None
    try:
        symlink = os.readlink(path)
    except OSError:
        pass

    return (path,open(path).read(),symlink)

def repr_dirtree(path):
    """Return a set completely representing a directory tree."""

    # Filecmp.dircmp would be nice to use, but it doesn't seem to be recursive,
    # and doesn't treat symlinks to files and the files themselves as
    # different things.

    # We use a bit of a brute force approach. The directory tree is walked and
    # we get a representation of every file in it with repr_file() This
    # includes the files full text.

    old_pwd = os.getcwd()
    os.chdir(path)

    r = set(())

    for root, dirs, files in os.walk('.'):
        for f in files:
            r.add(repr_file(os.path.join(root,f)))

    os.chdir(old_pwd)
    return frozenset(r)

def check_dataset(name):
    """Check that the working dataset is identical to a given dataset.
    
    By identical we mean that every files contents are the same and the
    directory structure is the same. Symlinks are considered to be different
    than the files they point to.
    """

    return repr_dirtree(dataset_path(name)) == repr_dirtree(tmpd)

def fcmp(obs,exp,eps=1e-6):
    """Tests whether two floating point numbers are approximately equal.

    Checks whether the distance is within epsilon relative to the value
    of the sum of observed and expected."""

    #try the cheap comparison first
    if obs == exp:
        return True

    sum = float(obs + exp)
    diff = float(obs - exp)

    # Very small sums get handled absolutely
    if abs(sum) < abs(eps):
        if abs(diff) > abs(eps):
            return False
        else:
            return True

    # Larger ones relatively
    if abs(diff/sum) > abs(eps):
        return False
    else:
        return True

def vert_equal(a,b):
    """Utility function to check if two lists of vertexes are approximetely equal."""
    if len(a) != len(b):
        return False
    for v1,v2 in zip(a,b):
        if len(v1) != len(v2):
            return False
        if not (fcmp(v1[0,0],v2[0,0]) and
                fcmp(v1[0,1],v2[0,1])):
            return False
    return True
