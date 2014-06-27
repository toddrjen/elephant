# -*- coding: utf-8 -*-
"""
docstring goes here.

:copyright: Copyright 2014 by the Elephant team, see AUTHORS.txt.
:license: Modified BSD, see LICENSE.txt for details.
"""

import unittest

import neo
import numpy as np
from numpy.testing.utils import assert_array_almost_equal
import quantities as pq

import elephant.statistics as es
import elephant.compat as cm


class isi_cv_TestCase(unittest.TestCase):
    def setUp(self):
        self.test_array_regular = np.arange(1, 6)

    def test_cv_isi_regular_spiketrain_is_zero(self):
        st = neo.SpikeTrain(self.test_array_regular,  units='ms', t_stop=10.0)
        targ = 0.0
        res = cm.cv(es.isi(st))
        self.assertEqual(res, targ)

    def test_cv_isi_regular_array_is_zero(self):
        st = self.test_array_regular
        targ = 0.0
        res = cm.cv(es.isi(st))
        self.assertEqual(res, targ)


if __name__ == '__main__':
    unittest.main()
