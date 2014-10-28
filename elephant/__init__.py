# -*- coding: utf-8 -*-
"""
Elephant is a package for the analysis of neurophysiology data, based on Neo.

:copyright: Copyright 2014 by the Elephant team, see AUTHORS.txt.
:license: Modified BSD, see LICENSE.txt for details.
"""

from . import conversion
from . import file_tools
from . import general_tools
from . import neo_tools
from . import neo_file_tools
from . import statistics


try:
    from . import pandas_bridge
except ImportError:
    pass
