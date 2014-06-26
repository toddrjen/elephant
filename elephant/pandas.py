# -*- coding: utf-8 -*-

import functools

import numpy as np
import pandas as pd


def _extract_attrs(obj, parents=True):
    """Given a neo object, return a dictionary of attributes and annotations.
    If parents is True, also include attributes and annotations from parent
    objects.  Priority is given to the attributes of child objects over
    those of parent objects"""

    attrs = obj.attributes
    for attr in obj._necessary_attrs + obj._recommended_attrs:
        attr = attr[0]
        if attr == getattr(obj, '_quantity_attr', None):
            continue
        attrs[attr] = getattr(obj, attr, None)

    for key, value in attrs.items():
        if (hasattr(attr, '__iter__') and not hasattr(attr, 'lower') and
                getattr(attr, 'ndim', 1) > 0):
            del attrs[attr]

    if parents:
        for parent in getattr(obj, 'parents', []):
            for key, value in _extract_attrs(parent, parents=True).items():
                if attrs.get(key, None) is None:
                    attrs[key] = value

    return attrs


def _multiindex_from_attrs(attrs):
    """Given a dictionary of attributes, return a MultiIndex"""
    return pd.MultiIndex.from_tuples([attrs.values()], names=attrs.keys())


def _sort_inds(obj, axis=0):
    """Put the indexes of a pandas DataFrame in sorted order"""
    obj.sortlevel(0, inplace=True, axis=axis, sort_remaining=True)


def spiketrain_to_dataframe(spiketrain, parents=True):
    """ Given a ``neo.core.SpikeTrain`` object, return a ``pandas.DataFrame``
    object.  The ``pandas.DataFrame`` object has a single column, with
    each element being the spike time converted to a ``numpy.timedelta64``
    object.  The column heading is a ``pandas.MultiIndex`` with one index
    for each of the scalar attributes and annotations.  The ``index``
    is the spike number.

    If :arg:``parents`` is ``True`` (default), also includes the attributes
    and annotations from any defined parent objects.  When attributes or
    annotations differ, preference is given to the attributes and annotations
    of children over those of parents (unless the attribute or annotation
    value is None).
    """
    attrs = _extract_attrs(spiketrain, parents=True)
    columns = _multiindex_from_attrs(attrs)

    times = spiketrain.rescale('s').magnitude[np.newaxis].T

    pdobj = pd.DataFrame(times, columns=columns)
    _sort_inds(pdobj, axis=1)
    pdobj.index.set_names(['spike_number'], inplace=True)

    return pdobj


def event_to_dataframe(evt, parents=True):
    """ Given a ``neo.core.Event`` object, return a ``pandas.DataFrame``
    object.  The ``pandas.DataFrame`` object has a single column, with
    each element being the event label.  The column heading is a
    ``pandas.MultiIndex`` with one index for each of the scalar attributes and
    annotations.  The index is the time of the corresponding event as
    a ``numpy.timedelta64`` dtype.

    If :arg:``parents`` is ``True`` (default), also includes the attributes
    and annotations from any defined parent objects.  When attributes or
    annotations differ, preference is given to the attributes and annotations
    of children over those of parents (unless the attribute or annotation
    value is None).
    """
    attrs = _extract_attrs(evt, parents=True)
    columns = _multiindex_from_attrs(attrs)

    times = evt.times.rescale('s').magnitude[np.newaxis].T
    labels = evt.labels[np.newaxis].T

    pdobj = pd.DataFrame(labels, index=times, columns=columns)
    _sort_inds(pdobj, axis=1)
    pdobj.index.set_names(['time'], inplace=True)

    return pdobj


def epoch_to_dataframe(epc, parents=True):
    """ Given a ``neo.core.Event`` object, return a ``pandas.DataFrame``
    object.  The ``pandas.DataFrame`` object has a single column, with
    each element being the epoch label.  The column heading is a
    ``pandas.MultiIndex`` with one index for each of the scalar attributes and
    annotations.  The index is a ``pandas.MultiIndex``, with the first index
    being the time of the corresponding event as a ``numpy.timedelta64`` dtype
    and the second being the duration of the corresponding event as a
    ``numpy.timedelta64`` dtype.

    If :arg:``parents`` is ``True`` (default), also includes the attributes
    and annotations from any defined parent objects.  When attributes or
    annotations differ, preference is given to the attributes and annotations
    of children over those of parents (unless the attribute or annotation
    value is None).
    """
    attrs = _extract_attrs(epc, parents=True)
    columns = _multiindex_from_attrs(attrs)

    times = epc.times.rescale('s').magnitude[np.newaxis].T
    durs = epc.durations.rescale('s').magnitude[np.newaxis].T

    index = np.MultiIndex.from_arrays([times, durs], names=['times',
                                                            'durations'])
    labels = epc.labels[np.newaxis].T

    pdobj = pd.DataFrame(labels, index=index, columns=columns)
    _sort_inds(pdobj, axis=1)
    pdobj.index.set_names(['time'], inplace=True)

    return pdobj


def analogsignal_to_dataframe(sig, parents=True):
    """ Given a ``neo.core.AnalogSignal`` object, return a ``pandas.DataFrame``
    object.  Only 1D and 2D analogsignals are supported.  For 3D, see
    ``analogsignal_to_panel``.  4D+ is not currently supported.
    The ``pandas.DataFrame`` object has one column for each
    row of the AnalogSignal.  The units of the AnalogSignal, if any,
    are converted to the base unit (e.g. ns to s, mm to m, uV to V).
    The column heading is a ``pandas.MultiIndex`` with one index for each of
    the scalar attributes and annotations.  Each ``channel_index`` element
    is set as the value of the corresponding ``channel_index`` column index.
    The index is the time of the data point as a ``numpy.timedelta64`` dtype.

    If :arg:``parents`` is ``True`` (default), also includes the attributes
    and annotations from any defined parent objects.  When attributes or
    annotations differ, preference is given to the attributes and annotations
    of children over those of parents (unless the attribute or annotation
    value is None).
    """
    attrs = _extract_attrs(sig, parents=True)
    columns = _multiindex_from_attrs(attrs)

    values = sig.rescale(sig.units.simplified.units).magnitude
    if values.ndim == 1:
        values = values[np.newaxis]
    elif values.ndim != 2:
        raise IndexError('Only 1D and 2D AnalogSignals are allowed')
    values = values.T

    times = sig.times.rescale('s').magnitude[np.newaxis].T
    durs = sig.durations.rescale('s').magnitude[np.newaxis].T

    index = np.MultiIndex.from_arrays([times, durs], names=['times',
                                                            'durations'])
    labels = sig.labels[np.newaxis].T

    pdobj = pd.DataFrame(labels, index=index, columns=columns)
    _sort_inds(pdobj, axis=1)
    pdobj.index.set_names(['time'], inplace=True)

    return pdobj


def _get_wrapped_function(func, levels, axis=0, **kwargs):
    """ Get a wrapper version of the function that can be applied to a pandas
    Grouper object
    """
    if kwargs and not levels:
        return functools.partial(func, **kwargs)

    def newfunc(pdobj):
        leveldict = {}
        if axis < 0 or axis > pdobj.ndim:
            raise IndexError('Invalid axis %s' % axis)

        if pdobj.ndim == 1:
            pdobj.apply(func)
            return
        elif pdobj.ndim == 2:
            if axis == 0:
                inds = pdobj.columns
            elif axis == 1:
                inds = pdobj.index
        elif pdobj.ndim == 3:
            if axis == 0:
                inds = pdobj.items
            if axis == 1:
                inds = pdobj.index
            elif axis == 2:
                inds = pdobj.columns

        for level in levels:
            if level in kwargs:
                continue
            value = inds.get_level_values(level).unique()
            if len(value) > 1:
                raise ValueError('Only one %s value is allowed' % level)
            kwargs[level] = value[0]
        func = functools.partial(func, **kwargs)
        pdobj.apply(func, axis=axis)

    return newfunc


def apply_function(pdobj, func, axis=0, **kwargs):
    """Apply an elephant function to a DataFrame created from a neo object.

    Index values taking from neo objects will be automatically used for doing
    the analysis.

    Parameters
    ----------
    pdobj : pandas Series, DataFrame, or Panel
            If a DataFrame that is created from a neo object using one of the
            conversion functions provided by this module, neo object attributes
            will be automatically used.
    func : python function
           The function to apply to the DataFrame.
    axis : int, optional
           The axis to apply the function over.  Defaults to 0 (columns).
           This only works with a DataFrame or Panel.
    kwargs : any, optional
             Additional arguments to provide to the `func`.

    Returns
    -------

    pdobj : scalar, pandas Series, DataFrame, or Panel
           The returned data type depends on the function used.
           Functions that reduce the number of axes will change the type
           (e.g. Series -> scalar, DataFrame -> Series).

    """
    from .. import neo_arguments
    levels = neo_arguments.get(func, [])
    func = _get_wrapped_function(func, levels, axis=axis, **kwargs)
    if levels:
        if pdobj.ndim == 1:
            raise IndexError('Cannot apply by levels on a Series')
        pdobj.groupby(levels=levels, axis=axis).apply(func)
    else:
        pdobj.apply(func, axis=axis)


def slice_spiketrain(pdobj, t_start=None, t_stop=None, axis=0):
    """Slice a pandas.DataFrame`` containing spike times.
    This sets the ``t_start`` and ``t_stop`` indices to be the new correct
    values."""
    pdobj.time_slace(t_start, t_stop)
    pdobj = pdobj.T.reset_index(['t_start', 't_stop'])
    pdobj['t_start'] = t_start
    pdobj['t_stop'] = t_stop
    return pdobj.set_index(['t_start', 't_stop']).T
