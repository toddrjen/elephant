# -*- coding: utf-8 -*-
"""
docstring goes here.

:copyright: Copyright 2014 by the Elephant team, see AUTHORS.txt.
:license: Modified BSD, see LICENSE.txt for details.
"""

from __future__ import division, print_function


def filter_strings(targs, filters):
    """Apply a list of string or regex-based filters to a list of strings.

    Filters are applied in-place, so it is suitable to remove directories
    from `os.walk`.

    Returns only strings that match all filters.

    Paremeters
    ----------

    targs : list of str objects
            A list of strings to filter.
    filters : str, regex object, or list of str and/or regex objects
              A list of strings and/or regular expressions to use as filters.

    Returns
    -------

    nothing
        Changes are made to `targ` in-place.

    """
    if hasattr(filters, 'lower'):
        for name in targs[:]:
            if filters not in name:
                targs.remove(name)
        return

    if hasattr(filters, 'search'):
        for name in targs[:]:
            if filters.search(name) is None:
                targs.remove(name)
        return

    for filt in filters:
        filter_strings(targs, filt)


def iter_flattened(objs, flat_ndarray=False):
    """A helper function flatten a structure to an iterable.

    The flattening is recursive.  This is slower than
    `list(itertools.chain.from_iterable())`, so it is probably better to use
    that when non-recursive flattening is needed.

    Parameters
    ----------

    objs : an object, list, dict, or other iterable or mapping
           The structure to flatten.
    flat_ndarray : bool, optional
                   If False (default), do not flatten numpy arrays or numpy
                   array subclasses.
                   If True, flatten them.

    Returns
    -------

    iterable
        An iterable of all the non-iterable, non-mapping objects in `objs`
        recursively.

    Notes
    -----

    Despite being iterable, strings are returned as-is.

    """
    if hasattr(objs, 'values') and not hasattr(objs, 'ndim'):
        for obj in iter_flattened(objs.values()):
            yield obj

    elif (hasattr(objs, '__iter__') and
          not hasattr(objs, 'lower') and
          (flat_ndarray or not hasattr(objs, 'ndim'))):
        for obj in objs:
            for iobj in iter_flattened(obj):
                yield iobj

    else:
        yield objs
