# -*- coding: utf-8 -*-
"""
docstring goes here.

:copyright: Copyright 2014 by the Elephant team, see AUTHORS.txt.
:license: Modified BSD, see LICENSE.txt for details.
"""

from __future__ import division, print_function

import os
import os.path

import neo

from elephant.general_tools import filter_strings, iter_flattened


def filter_by_extensions(filenames, extensions):
    """Filter a list of files by their extension.

    Filters are applied in-place.

    Returns only strings that have one of the given extensions.

    Paremeters
    ----------

    filenames : list of str objects
                A list of file names or paths to filter.
    extensions : str or list of str objects
                 A list of extensions to filter.
                 If any does not start with '.', it is automatically added.

    Returns
    -------

    nothing
        Changes are made to `filenames` in-place.

    """

    if hasattr(extensions, 'lower'):
        extensions = [extensions]

    extensions = ['.'+ext if ext[0] == '.' else ext for ext in extensions]

    for name in filenames[:]:
        if os.path.splitext(name)[1] not in extensions:
            filenames.remove(name)


def yield_files_paths(targdir=None, rescursive=False,
                      extensions=None, filefilters=None, dirfilters=None,
                      followlinks=False):
    """Read files from a directory as an iterator.

    Files can be read only from the current directory or recursively.  All
    compatible files can be read or only files with a particular extension
    or meeting particular criteria.

    Returns an iterable over the file paths.  The path is rooted in the
    starting directory.

    Parameters
    ----------

    targdir : str, optional
              The root directory to search for files.  Defaults to the current
              directory.
    recursive : bool, optional
                If False (default) only find files in the current directory.
                If True, also search subdirectories.
    extensions : list of str objects
                 If specified, only load files with the given extension.
                 By default, all files that can be read by `neo` are loaded.
    filefilters : str, list, or regular expression object, optional
                  If a str, only include files containing that substring
                  If a regular expression object, only includes files
                  matching that regular expression.
                  If a list, apply all items of the list according to the above
                  rules.
    dirfilters : str, list, or regular expression object, optional
                 If a str, only search directories containing that substring
                 If a regular expression object, only search directories
                 matching that regular expression.
                 If a list, apply all items of the list according to the above
                 rules.
                 Only applied to directories below `targdir`.
                 Does nothing if `recursive` is False.
    followlinks : bool, optional
                  If False (default) don't follow symlinks when descending into
                  child directories.
                  If True, follow symlinks.
                  Does nothing if `recursive` is False.

    Returns
    -------

    iterator of str
        An iterator over the paths.  The paths are rooted in `targdir`

    Notes
    -----

    Be aware that setting followlinks to True can lead to infinite recursion if
    a link points to a parent directory of itself. This function does not keep
    track of the directories it visited already.

    """
    if targdir is None:
        targdir = os.curdir

    for dirpath, dirnames, filenames in os.walk(targdir,
                                                followlinks=followlinks):

        filter_by_extensions(filenames, extensions)
        filter_strings(filenames, filefilters)

        for name in filenames:
            yield os.path.join(dirpath, name)

        if not rescursive:
            break

        filter_strings(dirnames, dirfilters)
