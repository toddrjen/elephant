# -*- coding: utf-8 -*-
"""
docstring goes here.

:copyright: Copyright 2014 by the Elephant team, see AUTHORS.txt.
:license: Modified BSD, see LICENSE.txt for details.
"""

from __future__ import division, print_function

from itertools import chain

import neo
from neo.core.container import unique_objs

from elephant.file_tools import yield_files_paths
from elephant.general_tools import iter_flattened


def extract_neo_attrs(obj, parents=True, child_first=True,
                      skip_array=False, skip_none=False):
    """Given a neo object, return a dictionary of attributes and annotations.

    Parameters
    ----------

    obj : neo object
    parents : bool, optional
              Also include attributes and annotations from parent neo
              objects (if any).
    child_first : bool, optional
                  If True (default True), values of child attributes are used
                  over parent attributes in the event of a name conflict.
                  If False, parent attributes are used.
                  This parameter does nothing if `parents` is False.
    skip_array : bool, optional
                 If True (default False), skip attributes that store non-scalar
                 array values.
    skip_none : bool, optional
                If True (default False), skip annotations and attributes that
                have a value of `None`.

    Returns
    -------

    dict
        A dictionary where the keys are annotations or attribute names and
        the values are the corresponding annotation or attribute value.

    """
    attrs = obj.annotations.copy()
    for attr in obj._necessary_attrs + obj._recommended_attrs:
        if skip_array and len(attr) >= 3 and attr[2]:
            continue
        attr = attr[0]
        if attr == getattr(obj, '_quantity_attr', None):
            continue
        attrs[attr] = getattr(obj, attr, None)

    if skip_none:
        for attr, value in attrs.copy().items():
            if value is None:
                del attrs[attr]

    if not parents:
        return attrs

    for parent in getattr(obj, 'parents', []):
        if parent is None:
            continue
        newattr = extract_neo_attrs(parent, parents=True,
                                    child_first=child_first,
                                    skip_array=skip_array,
                                    skip_none=skip_none)
        if child_first:
            newattr.update(attrs)
            attrs = newattr
        else:
            attrs.update(newattr)

    return attrs


def get_all_objs(container, classname=None):
    """Get all `neo` objects of a given type from a container.

    The objects can be any list, dict, or other iterable or mapping containing
    neo objects, as well as any neo object that can hold the object.
    Can be used to either get all neo objects or only those of a particular
    type.
    Objects are searched recursively, so the objects can be nested
    (such as a list of blocks).

    Parameters
    ----------

    container : list, tuple, iterable, dict, neo container
                The container for the neo objects.
    classname : str, optional
                The name of the class, with proper capitalization
                (so `SpikeTrain`, not `Spiketrain` or `spiketrain`)
                If not specified, all neo objects are returned.

    Returns
    -------

    list
        A list of unique `neo` objects

    """
    if not hasattr(container, 'file_origin'):
        vals = list(iter_flattened(container))
        if len(vals) == 1 and vals[0] is container:
            raise TypeError('Cannot handle object of type %s' %
                            type(container))
        vals = (get_all_objs(obj, classname) for obj in vals)
        vals = list(chain.from_iterable(vals))
    elif classname is None:
        vals = [container]
        if hasattr(container, 'children_recur'):
            vals.extend(container.children_recur)
        else:
            return vals
    elif container.__class__.__name__ == classname:
        return [container]
    else:
        classholder = classname.lower() + 's'
        if hasattr(container, classholder):
            vals = getattr(container, classholder)
        elif hasattr(container, 'list_children_by_class'):
            vals = container.list_children_by_class(classname)
        else:
            raise TypeError('Cannot handle object of type %s' %
                            type(container))
    return unique_objs(vals)


def set_all_attrs(neoobj, attr, value, create=False):
    """Set a neo object and all of its children to have a given attribute.

    Can also work on a list, dict, or other iterable of neo objects.

    The attribute changes happen in-place.

    Paramters
    ---------

    neoobj : a neo object, or a list, dict, or iterable of neo objects
             The objects whose attributes should be set.
    attr : str or list of str objects
           The name of the attribute to set or a list of names to set.
    value : any
            The value to set `attr` to.
    create : bool, optional
             If False (default) only set objects that already have an attribute
             named `attr`.
             If True, create `attr` if it is not already defined.

    Returns
    -------

    nothing
        Changes to `obj` happen in-place.

    """
    for obj in get_all_objs(neoobj):
        if create or hasattr(obj, attr):
            setattr(obj, attr, value)
        for child in getattr(obj, 'children_recur', []):
            if create or hasattr(obj, attr):
                setattr(obj, attr, value)


def get_all_spiketrains(container):
    """Get all `neo.Spiketrain` objects from a container.

    The objects can be any list, dict, or other iterable or mapping containing
    spiketrains, as well as any neo object that can hold spiketrains:
    `neo.Block`, `neo.RecordingChannelGroup`, `neo.Unit`, and `neo.Segment`.

    Containers are searched recursively, so the objects can be nested
    (such as a list of blocks).

    Parameters
    ----------

    container : list, tuple, iterable, dict,
                neo Block, neo Segment, neo Unit, neo RecordingChannelGroup
                The container for the spiketrains.

    Returns
    -------

    list
        A list of the unique `neo.SpikeTrain` objects in `container`.

    """
    return get_all_objs(container, 'SpikeTrain')


def get_all_events(container):
    """Get all `neo.Event` objects from a container.

    The objects can be any list, dict, or other iterable or mapping containing
    events, as well as any neo object that can hold events:
    `neo.Block` and `neo.Segment`.

    Containers are searched recursively, so the objects can be nested
    (such as a list of blocks).

    Parameters
    ----------

    container : list, tuple, iterable, dict, neo Block, neo Segment
                The container for the events.

    Returns
    -------

    list
        A list of the unique `neo.Event` objects in `container`.

    """
    return get_all_objs(container, 'Event')


def get_all_epochs(container):
    """Get all `neo.Epoch` objects from a container.

    The objects can be any list, dict, or other iterable or mapping containing
    epochs, as well as any neo object that can hold epochs:
    `neo.Block` and `neo.Segment`.

    Containers are searched recursively, so the objects can be nested
    (such as a list of blocks).

    Parameters
    ----------

    container : list, tuple, iterable, dict, neo Block, neo Segment
                The container for the epochs.

    Returns
    -------

    list
        A list of the unique `neo.Epoch` objects in `container`.

    """
    return get_all_objs(container, 'Epoch')


def read_all_generic(ioobj):
    """Reads all objects from a `neo.io` object in a consistent manner.

    Reads from `read_all_blocks` if available.
    If not, reads from `read_all_segments` if available.
    If not, just does `read`, and puts the result in a list.

    Can either be given a filename or an existing io object to read from.

    Parameters
    ----------

    ioobj : str or `neo.io` object
            The file or io object to read from.

    Returns
    -------

    list
        A list of one or more `neo.core.Block` or `neo.core.Segment` objects.

    """
    if hasattr(ioobj, 'lower'):
        ioobj = neo.io.get_io(ioobj)

    if hasattr(ioobj, 'read_all_blocks'):
        return ioobj.read_all_blocks()
    elif hasattr(ioobj, 'read_all_segments'):
        return ioobj.read_all_segments()
    else:
        return [ioobj.read()]


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
