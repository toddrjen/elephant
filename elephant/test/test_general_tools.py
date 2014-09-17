# -*- coding: utf-8 -*-
"""
docstring goes here.

:copyright: Copyright 2014 by the Elephant team, see AUTHORS.txt.
:license: Modified BSD, see LICENSE.txt for details.
"""

import re
import unittest

import numpy as np

# use `gtl` instead of `gt` to avoid confusion with `greater-than`
import elephant.general_tools as gtl


class FilterStringsTestCase(unittest.TestCase):
    def setUp(self):
        self.strlist = ['spam', 'spams', 'spam01', 'SpAm200',
                        'spam_eggs',
                        'egg', 'eggs', 'eggs01', 'egg01a', 'EgG201', 'eGgs100']

    def test__filter_strings__str_single(self):
        ops = 'eggs'
        targ = ['spam_eggs', 'eggs', 'eggs01']

        gtl.filter_strings(self.strlist, ops)

        self.assertEqual(targ, self.strlist)

    def test__filter_strings__str_multi(self):
        ops = ['eggs', 'spam']
        targ = ['spam_eggs']

        gtl.filter_strings(self.strlist, ops)

        self.assertEqual(targ, self.strlist)

    def test__filter_strings__str_single_none(self):
        ops = 'EGGS'
        targ = []

        gtl.filter_strings(self.strlist, ops)

        self.assertEqual(targ, self.strlist)

    def test__filter_strings__str_multi_none(self):
        ops = ['201', 'spam']
        targ = []

        gtl.filter_strings(self.strlist, ops)

        self.assertEqual(targ, self.strlist)

    def test__filter_strings__regex_single(self):
        ops = re.compile('\D\d\d$')
        targ = ['spam01', 'eggs01']

        gtl.filter_strings(self.strlist, ops)

        self.assertEqual(targ, self.strlist)

    def test__filter_strings__regex_single_none(self):
        ops = re.compile('\D\d\d\d\d$')
        targ = []

        gtl.filter_strings(self.strlist, ops)

        self.assertEqual(targ, self.strlist)

    def test__filter_strings__regex_multi(self):
        ops = [re.compile('\D\d\d$'), re.compile('^e')]
        targ = ['eggs01']

        gtl.filter_strings(self.strlist, ops)

        self.assertEqual(targ, self.strlist)

    def test__filter_strings__regex_multi_none(self):
        ops = [re.compile('\D\d\d$'), re.compile('^E')]
        targ = []

        gtl.filter_strings(self.strlist, ops)

        self.assertEqual(targ, self.strlist)

    def test__filter_strings__both_multi(self):
        ops = ['egg', re.compile('^s')]
        targ = ['spam_eggs']

        gtl.filter_strings(self.strlist, ops)

        self.assertEqual(targ, self.strlist)

    def test__filter_strings__both_multi_none(self):
        ops = ['spam', re.compile('^e')]
        targ = []

        gtl.filter_strings(self.strlist, ops)

        self.assertEqual(targ, self.strlist)

    def test__filter_strings__emptylist(self):
        ops = []
        targ = self.strlist[:]

        gtl.filter_strings(self.strlist, ops)

        self.assertEqual(targ, self.strlist)

    def test__filter_strings__Nonelist(self):
        ops = None
        targ = self.strlist[:]

        gtl.filter_strings(self.strlist, ops)

        self.assertEqual(targ, self.strlist)

    def test__filter_strings__emptystring(self):
        ops = ''
        targ = self.strlist[:]

        gtl.filter_strings(self.strlist, ops)

        self.assertEqual(targ, self.strlist)


class IterFlattenedTestCase(unittest.TestCase):
    def setUp(self):
        self.nestedobj = [[0, (1, 2), 3], (4, {'a': [5, (6, {'b': 7})]}),
                          '8', '9', '10', ([[[((11,),)]]],),
                          np.array(12), np.array([13]), np.array([14, 15, 16]),
                          np.array([[17, 18], [19, 20]])]

    def test__iter_flattened__no_flat_ndarray(self):
        targ = [0, 1, 2, 3, 4, 5, 6, 7, '8', '9', '10', 11,
                np.array(12), np.array([13]), np.array([14, 15, 16]),
                np.array([[17, 18], [19, 20]])]

        res0 = list(gtl.iter_flattened(self.nestedobj, flat_ndarray=False))
        res1 = list(gtl.iter_flattened(self.nestedobj))

        self.assertEqual(targ[:12], res0[:12])
        self.assertEqual(targ[:12], res1[:12])

        np.testing.assert_array_equal(targ[12], res0[12])
        np.testing.assert_array_equal(targ[13], res0[13])
        np.testing.assert_array_equal(targ[14], res0[14])

    def test__iter_flattened__flat_ndarray(self):
        targ = [0, 1, 2, 3, 4, 5, 6, 7, '8', '9', '10', 11,
                12, 13, 14, 15, 16, 17, 18, 19, 20]

        res0 = list(gtl.iter_flattened(self.nestedobj, flat_ndarray=True))

        self.assertEqual(targ, res0)

if __name__ == '__main__':
    unittest.main()
