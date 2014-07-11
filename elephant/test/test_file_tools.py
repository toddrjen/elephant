# -*- coding: utf-8 -*-
"""
docstring goes here.

:copyright: Copyright 2014 by the Elephant team, see AUTHORS.txt.
:license: Modified BSD, see LICENSE.txt for details.
"""

import os
import os.path
import tempfile
import unittest

from neo.io import NeoHdf5IO, PickleIO
#from neo.io import NeoHdf5IO, NeoMatlabIO, PickleIO
from neo.test.generate_datasets import fake_neo

import elephant.file_tools as ft

TEMP_FORMATS = {'.h5': NeoHdf5IO,
                #'.mat': NeoMatlabIO,
                '.pkl': PickleIO}

DEPTH = 5


def create_local_temp_dir(name, directory=None):
    """
    Create a directory for storing temporary files needed for testing elephant.

    Parameters
    ----------

    name : str
           The name of the subdirectory to create for the current test.
    directory : str, optional
                The directory to put the `name` directory in.
                Defaults to automatically create the directory in
                {tempdir}/files_for_testing_elephant on linux/unix/mac or
                {tempdir}\files_for_testing_elephant on windows, where
                {tempdir} is the system temporary directory returned by
                tempfile.gettempdir().

    Returns
    -------

    str
        The path to the new directory.

    """
    if directory is None:
        directory = os.path.join(tempfile.gettempdir(),
                                 'files_for_testing_elephant')

    if not os.path.exists(directory):
        os.mkdir(directory)
    directory = os.path.join(directory, name)
    if not os.path.exists(directory):
        os.mkdir(directory)
    return directory


def _make_temp_structure(tempdir, n=None, depth=None, link=False):
    """Make a temporary file structure of neo files.

    Parameters
    ----------

    tempdir : str
              The directory to put the files in.
    n : int, optional
        The number of files and directories to put at each level.
        Defaults to the length of `elephant.test.test_file_tools.TEMP_FORMATS`,
        which is 3 currently.
    depth : int, optional
            The number of levels of subdirectories to make below `tempdir`.
            Defaults to elephant.test.test_file_tools.DEPTH`,
            which is 5 currently.
            If 0, create no subdirectories.
    link : bool, optional
           If True, also create `n` symlinked versions of each directory at
           each level.
           If False (default), no symlinks are created.
           Does not work on all combinations of python version and
           operating system.  On operating that don't support it, no symlinks
           are created even if this is set to True.

    Returns
    -------

    paths : list
        A sorted list of the files in `tempdir`, rooted in `tempdir`.
    allpaths : list
        A sorted list of the files in `tempdir` and all subdirectories of
        `tempdir`, rooted in `tempdir`.  Excludes symlinked directories.
        This is the same `paths` if `recursive` is False.
    linkpaths : list
        A sorted list of the files in `tempdir` and all subdirectories and
        symlinked subdirectories of `tempdir`, rooted in `tempdir`.
        This is the same `paths` and `allpaths` if `recursive` is False.
        This is the same as `allpaths` if `link` is False.

    """
    if n is None:
        n = len(TEMP_FORMATS)

    if depth is None:
        depth = DEPTH

    paths = []

    for i in range(n):
        ext = TEMP_FORMATS.keys()[n]
        ioclass = TEMP_FORMATS[ext]

        path = os.path.join(tempdir, 'block_%s%s' % (i, ext))
        iobj = ioclass(path)
        iobj.write_block(fake_neo('Block', n=3))
        try:
            iobj.close()
        except:
            pass

        paths.append(path)

    paths = sorted(paths)
    allpaths = paths[:]
    linkpaths = paths[:]

    if depth > 0:
        for i in range(n):
            tempdir = os.path.join(tempdir, 'dir_%s' % i)
            _, paths2 = _make_temp_structure(n=n, depth=depth-1,
                                             tempdir=tempdir)
            allpaths.extend(paths2)
            linkpaths.extend(paths2)

            if not link:
                continue
            try:
                linkdir = tempdir+'_l'
                os.symlink(tempdir, linkdir)
            except:
                pass
            else:
                paths3 = [path.replace(tempdir, linkdir) for path in paths2]
                linkpaths.extend(paths3)

    return paths, sorted(allpaths), sorted(linkpaths)


class yield_files_paths_TestCase(unittest.TestCase):
    def setUp(self):
        self.targdir = TARGDIR
        self.paths = PATHS
        self.allpaths = ALLPATHS
        self.linkpaths = LINKPATHS

        if hasattr(self, 'assertItemsEqual'):
            self.assertCountEqual = self.assertItemsEqual

    def test_default(self):
        res0 = ft.yield_files_paths(targdir=self.targdir)
        res1 = ft.yield_files_paths(targdir=self.targdir, rescursive=False)
        res2 = ft.yield_files_paths(targdir=self.targdir, extensions=None)
        res3 = ft.yield_files_paths(targdir=self.targdir, extensions=[])
        res4 = ft.yield_files_paths(targdir=self.targdir, filefilter=None)
        res5 = ft.yield_files_paths(targdir=self.targdir, filefilter=[])
        res6 = ft.yield_files_paths(targdir=self.targdir, dirfilter=None)
        res7 = ft.yield_files_paths(targdir=self.targdir, dirfilter=[])
        res8 = ft.yield_files_paths(targdir=self.targdir, followlinks=False)
        res9 = ft.yield_files_paths(targdir=self.targdir, followlinks=True)

        res0 = list(res0)
        res1 = list(res1)
        res2 = list(res2)
        res3 = list(res3)
        res4 = list(res4)
        res5 = list(res5)
        res6 = list(res6)
        res7 = list(res7)
        res8 = list(res8)
        res9 = list(res9)

        targ = self.paths

        self.assertCountEqual(targ, res0)
        self.assertCountEqual(targ, res1)
        self.assertCountEqual(targ, res2)
        self.assertCountEqual(targ, res3)
        self.assertCountEqual(targ, res4)
        self.assertCountEqual(targ, res5)
        self.assertCountEqual(targ, res6)
        self.assertCountEqual(targ, res7)
        self.assertCountEqual(targ, res8)
        self.assertCountEqual(targ, res9)

    def test_recursive(self):
        res0 = ft.yield_files_paths(targdir=self.targdir, rescursive=True)
        res1 = ft.yield_files_paths(targdir=self.targdir, rescursive=True,
                                    extensions=None)
        res2 = ft.yield_files_paths(targdir=self.targdir, rescursive=True,
                                    extensions=[])
        res3 = ft.yield_files_paths(targdir=self.targdir, rescursive=True,
                                    filefilter=None)
        res4 = ft.yield_files_paths(targdir=self.targdir, rescursive=True,
                                    filefilter=[])
        res5 = ft.yield_files_paths(targdir=self.targdir, rescursive=True,
                                    dirfilter=None)
        res6 = ft.yield_files_paths(targdir=self.targdir, rescursive=True,
                                    dirfilter=[])
        res7 = ft.yield_files_paths(targdir=self.targdir, rescursive=True,
                                    followlinks=False)

        res0 = list(res0)
        res1 = list(res1)
        res2 = list(res2)
        res3 = list(res3)
        res4 = list(res4)
        res5 = list(res5)
        res6 = list(res6)
        res7 = list(res7)

        targ = self.allpaths

        self.assertCountEqual(targ, res0)
        self.assertCountEqual(targ, res1)
        self.assertCountEqual(targ, res2)
        self.assertCountEqual(targ, res3)
        self.assertCountEqual(targ, res4)
        self.assertCountEqual(targ, res5)
        self.assertCountEqual(targ, res6)
        self.assertCountEqual(targ, res7)

    def test_recursive_followlinks(self):
        res0 = ft.yield_files_paths(targdir=self.targdir,
                                    rescursive=True, followlinks=True)
        res1 = ft.yield_files_paths(targdir=self.targdir,
                                    rescursive=True, followlinks=True,
                                    extensions=None)
        res2 = ft.yield_files_paths(targdir=self.targdir,
                                    rescursive=True, followlinks=True,
                                    extensions=[])
        res3 = ft.yield_files_paths(targdir=self.targdir,
                                    rescursive=True, followlinks=True,
                                    filefilter=None)
        res4 = ft.yield_files_paths(targdir=self.targdir,
                                    rescursive=True, followlinks=True,
                                    filefilter=[])
        res5 = ft.yield_files_paths(targdir=self.targdir,
                                    rescursive=True, followlinks=True,
                                    dirfilter=None)
        res6 = ft.yield_files_paths(targdir=self.targdir,
                                    rescursive=True, followlinks=True,
                                    dirfilter=[])

        res0 = list(res0)
        res1 = list(res1)
        res2 = list(res2)
        res3 = list(res3)
        res4 = list(res4)
        res5 = list(res5)
        res6 = list(res6)

        targ = self.linkpaths

        self.assertCountEqual(targ, res0)
        self.assertCountEqual(targ, res1)
        self.assertCountEqual(targ, res2)
        self.assertCountEqual(targ, res3)
        self.assertCountEqual(targ, res4)
        self.assertCountEqual(targ, res5)
        self.assertCountEqual(targ, res6)


if __name__ == '__main__':
    TARGDIR = create_local_temp_dir('file_tools')
    PATHS, ALLPATHS, LINKPATHS = _make_temp_structure(tempdir=tempfile.tempdir)
    unittest.main()
