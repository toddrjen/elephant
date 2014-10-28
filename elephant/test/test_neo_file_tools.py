# -*- coding: utf-8 -*-
"""
docstring goes here.

:copyright: Copyright 2014 by the Elephant team, see AUTHORS.txt.
:license: Modified BSD, see LICENSE.txt for details.
"""

from __future__ import division, print_function, unicode_literals

from itertools import chain
import unittest

from neo.test.generate_datasets import fake_neo, get_fake_values
from neo.test.tools import assert_same_sub_schema
from numpy.testing.utils import assert_array_equal

import elephant.neo_file_tools as nf


class YieldNeoFilesFromFilenamesTestCase(unittest.TestCase):
    def test_neo_files_to_dict(self):
        pass
        #neo_files_to_dict()


class YieldNeoFilesFromDirTestCase(unittest.TestCase):
    def test_yield_neo_files_from_dir(self):
        pass
        #yield_neo_files_from_dir()


class NeoFilesToDictTestCase(unittest.TestCase):
    def test_neo_files_to_dict(self):
        pass
        #neo_files_to_dict()


class NeoObjectsToHDF5TestCase(unittest.TestCase):
    def test_neo_objects_to_hdf5(self):
        pass
        #neo_objects_to_hdf5()


class NeoFilesToHDF5TestCase(unittest.TestCase):
    def test_neo_files_to_hdf5(self):
        pass
        #neo_files_to_hdf5()


if __name__ == '__main__':
    unittest.main()
