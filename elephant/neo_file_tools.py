# -*- coding: utf-8 -*-
"""
Tools for working with `neo` files.

:copyright: Copyright 2014 by the Elephant team, see AUTHORS.txt.
:license: Modified BSD, see LICENSE.txt for details.
"""

from __future__ import division, print_function

import os.path

import neo

from .file_tools import yield_files_paths
from .general_tools import iter_flattened
from .neo_tools import read_all_generic, set_all_attrs


def yield_neo_files_from_filenames(filenames):
    """Read `neo`-compatible files from a list or iterable of file names.


    Returns an iterable over the `neo` objects.  The `file_origin` parameter
    can be used to retrieve the path name rooted in the starting directory.

    Parameters
    ----------

    filenames : str, list of str objects, or other container of str objects
                The filenames to read.  If a list, dict, or other container,
                the filenames are read recursively.

    Returns
    -------

    iterator of neo objects
    """
    for path in iter_flattened(filenames):
        for obj in read_all_generic(path):
            set_all_attrs(obj, 'file_origin', path)
            yield obj


def yield_neo_files_from_dir(targdir=None, rescursive=False,
                             extensions=None, filefilters=None,
                             dirfilters=None, followlinks=False):
    """Read `neo`-compatible files from a directory as an iterator.

    Files can be read only from the current directory or recursively.  All
    compatible files can be read or only files with a particular extension
    or meeting particular criteria.

    Returns an iterable over the `neo` objects.  The `file_origin` parameter
    can be used to retrieve the path name rooted in the starting directory.

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

    iterator of neo objects

    Notes
    -----

    The `file_origin` attribute of the neo objects includes the path rooted in
    to `targdir`.  It is applied to all objects.

    Be aware that setting followlinks to True can lead to infinite recursion if
    a link points to a parent directory of itself. This function does not keep
    track of the directories it visited already.

    """
    filenames = yield_files_paths(targdir=targdir, rescursive=rescursive,
                                  extensions=extensions,
                                  filefilters=filefilters,
                                  dirfilters=dirfilters,
                                  followlinks=followlinks)
    return yield_neo_files_from_filenames(filenames)


def neo_files_to_dict(targdir=None, rescursive=False,
                      extensions=None, filefilters=None, dirfilters=None,
                      followlinks=False):
    """Read `neo`-compatible files from a directory into a single dict.

    Files can be read only from the current directory or recursively.  All
    compatible files can be read or only files with a particular extension
    or meeting particular criteria.

    Returns a nested dictionary where keys are directories matching the
    directory structure read in.

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

    dict
        A nested dictionary containing the `neo` objects.
        Keys are directories.

    Notes
    -----

    The `file_origin` attribute of the neo objects includes the path rooted in
    to `targdir`.  It is applied to all objects.

    Be aware that setting followlinks to True can lead to infinite recursion if
    a link points to a parent directory of itself. This function does not keep
    track of the directories it visited already.

    """
    neoiter = yield_neo_files_from_dir(targdir=targdir, rescursive=rescursive,
                                       extensions=extensions,
                                       filefilters=filefilters,
                                       dirfilters=dirfilters,
                                       followlinks=followlinks)
    objdict = {}
    for neoobj in neoiter:
        path = os.path.split(neoobj.file_origin)
        curdict = objdict
        while len(path) > 1:
            if path[0] not in curdict:
                curdict[path[0]] = {}
                curdict = curdict[path[0]]
        if path[0] not in curdict:
            curdict[path[0]] = []
        curdict[path[0]].append(neoobj)

    return objdict


def neo_objects_to_hdf5(neoobjs, filename, flat=False, with_current=True):
    """Write multiple neo objects to an hdf5 file.

    Parameters
    ----------

    neoobjs : a neo object, list, dict, or other iterable with neo objects
              The neo object or objects objects to write to the file.
    filename : str
               The file to write `neoobjs` to.
    flat : bool, optional
           If False (default) the path of the neo objects in the hdf5 file
           matches the path in their `file_origin` attribute.
           If True a flat structure will be generated.
    with_current : bool, optional
                   If True (default) and the object already has an `hdf5_path`
                   attribute, append that to the end of the path.
                   If False, use only the file path.

    Returns
    -------

    Nothing

    Notes
    -----

    The 'hdf5_path` attribute is automatically set when the file is written,
    sof it is already present but `with_current` is False any existing value
    for that attribute will be overwritten.

    """
    ioobj = neo.io.NeoHdf5IO(filename)

    try:
        for obj in iter_flattened(neoobjs):
            path = obj.file_origin
            if flat or path is None:
                path = '/'
            else:
                path = path.lstrip('.').lstrip(os.sep)
                path = '/' + path

            if with_current:
                path += getattr(obj, 'hdf5_path', '')

            ioobj.save(obj, where=path)
    except BaseException:
        ioobj.close()
        raise

    ioobj.close()


def neo_files_to_hdf5(filename, targdir=None, rescursive=False,
                      extensions=None, filefilters=None, dirfilters=None,
                      followlinks=False, flat=False, with_current=True):
    """Read `neo`-compatible files from a directory into a single hdf5 file.

    Files can be read only from the current directory or recursively.  All
    compatible files can be read or only files with a particular extension
    or meeting particular criteria.

    Returns an iterable over the `neo` objects.  The `file_origin` parameter
    can be used to retrieve the path name rooted in the starting directory.

    Parameters
    ----------

    filename : str
               The file to write `neoobjs` to.
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
    flat : bool, optional
           If False (default) the path of the neo objects in the hdf5 file
           matches the path in their `file_origin` attribute.
           If True a flat structure will be generated.
    with_current : bool, optional
                   If True (default) and the object already has an `hdf5_path`
                   attribute, append that to the end of the path.
                   If False, use only the file path.

    Returns
    -------

    iterator of neo objects

    Notes
    -----

    The `file_origin` attribute of the neo objects includes the path rooted in
    to `targdir`.  It is applied to all objects.

    Be aware that setting followlinks to True can lead to infinite recursion if
    a link points to a parent directory of itself. This function does not keep
    track of the directories it visited already.

    The 'hdf5_path` attribute is automatically set when the file is written,
    sof it is already present but `with_current` is False any existing value
    for that attribute will be overwritten.

    """
    neoobjs = yield_neo_files_from_dir(targdir=targdir, rescursive=rescursive,
                                       extensions=extensions,
                                       filefilters=filefilters,
                                       dirfilters=dirfilters,
                                       followlinks=followlinks)
    neo_objects_to_hdf5(neoobjs, filename,
                        flat=flat, with_current=with_current)
