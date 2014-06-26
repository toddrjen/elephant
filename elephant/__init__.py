# -*- coding: utf-8 -*-

from . import statistics
from . import conversion


try:
    from . import pandas
except ImportError:
    pass


# this contains a dictionary with keys being functions and values being
# a list of arguments that can use neo attributes
# the neo attribute name and the function argument name should be identical
neo_arguments = {}
for module in [statistics, conversion, compat]:
    _args = getattr(module, 'neo_arguments', {})
    neo_arguments.update(_args)
