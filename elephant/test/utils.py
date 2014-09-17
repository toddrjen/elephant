# -*- coding: utf-8 -*-
"""
Helper functions for testing `elephant`.

:copyright: Copyright 2014 by the Elephant team, see AUTHORS.txt.
:license: Modified BSD, see LICENSE.txt for details.
"""

import os
import os.path
import tempfile

import neo
from neo.test.generate_datasets import fake_neo


TEMP_FORMATS = {'.h5': neo.io.NeoHdf5IO,
                # '.mat': neo.io.NeoMatlabIO,
                '.pkl': neo.io.PickleIO}

DEPTH = 5


def create_local_temp_dir(name, directory=None):
    r"""
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


def make_temp_structure(tempdir=None, formats=TEMP_FORMATS,
                        depth=None, link=False):
    """Make a temporary file structure of neo files.

    Parameters
    ----------

    tempdir : str, optional
              The directory to put the files in.
              If not specified or None, defaults to `tempfile.tempdir`.
    depth : int, optional
            The number of levels of subdirectories to make below `tempdir`.
            Defaults to elephant.test.test_file_tools.DEPTH`,
            which is 5 currently.
            If 0, create no subdirectories.
    formats : dict, optional
              A dictionary with keys being the extensions of the file types
              to create and the values being `neo.io` classes corresponding
              to the respective extension.
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
    if depth is None:
        depth = DEPTH

    if tempdir is None:
        tempdir = tempfile.tempdir

    paths = []

    for i, (ext, ioclass) in enumerate(formats.items()):
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
        for i, ext in enumerate(formats):
            tempdir = os.path.join(tempdir, 'dir_%s' % i)
            _, paths2 = make_temp_structure(depth=depth-1, tempdir=tempdir,
                                            formats=formats)
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
                paths3 = [ipath.replace(tempdir, linkdir) for ipath in paths2]
                linkpaths.extend(paths3)

    return paths, sorted(allpaths), sorted(linkpaths)
