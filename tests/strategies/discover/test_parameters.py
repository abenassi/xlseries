#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import nose
import os
from xlseries.strategies.discover.parameters import Parameters

"""
test_parameters
----------------------------------

This module tests the parameters object
"""


class ParametersTest(unittest.TestCase):

    def setUp(self):
        base_dir = os.path.dirname(__file__)
        self.params = Parameters(
            os.path.join(base_dir, "original", "test_params.json"))
        self.params_exp = Parameters(
            os.path.join(base_dir, "expected", "test_params.json"))

    def tearDown(self):
        del self.params

    # @unittest.skip("skip")
    def test_load_parameters(self):
        self.assertEqual(self.params.__dict__, self.params_exp.__dict__)

    # @unittest.skip("skip")
    def test_eval_param(self):
        self.assertEqual(self.params._eval_param("True"), True)

    # @unittest.skip("skip")
    def test_get_num_series(self):
        self.assertEqual(self.params._get_num_series(self.params.__dict__), 3)
        self.assertEqual(self.params._get_num_series({"param": None}), None)

    def test_apply_to_all(self):
        self.assertEqual(self.params._apply_to_all(True, 2), [True, True])
        self.assertEqual(self.params._apply_to_all(True, None), True)

    def test_unpack_header_ranges(self):

        exp = ["A5", "A6", "A7", "A8"]
        self.assertEqual(self.params._unpack_header_ranges("a5-A8"), exp)

        exp = ["A5", "B5", "C5"]
        self.assertEqual(self.params._unpack_header_ranges("A5-c5"), exp)

        exp = ["A5"]
        self.assertEqual(self.params._unpack_header_ranges("a5"), exp)

        exp = None
        self.assertEqual(self.params._unpack_header_ranges("None"), exp)


if __name__ == '__main__':
    nose.run(defaultTest=__name__)
