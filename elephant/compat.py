# -*- coding: utf-8 -*-
"""
Various functions to improve compatibility with NeuroTools.
Functions here should be considered deprecated and users of them should switch
to the alternative documented below.

cv : coefficient of variation, use scipy.stats.variation instead

:copyright: Copyright 2014 by the Elephant team, see AUTHORS.txt.
:license: Modified BSD, see LICENSE.txt for details.
"""

from __future__ import division, print_function

import scipy.stats


def cv(*args, **kwargs):
    """Coefficient of variation.

    This function is deprecated, please use `scipy.stats.variation` instead.

    The call signature of this function is identical to that of
    `scipy.stats.variation`
    """
    return scipy.stats.variation(*args, **kwargs)


# this contains a dictionary with keys being functions and values being
# a list of arguments that can use neo attributes
# the neo attribute name and the function argument name should be identical
neo_arguments = {}
