#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import nose
import os
import json
import copy

from xlseries.strategies.discover.parameters import Parameters

"""
test_parameters

This module tests the parameters object.
"""


def get_orig_params_path(file_name):
    base_dir = os.path.dirname(__file__)
    return os.path.join(base_dir, "original", file_name)


def get_exp_params_path(file_name):
    base_dir = os.path.dirname(__file__)
    return os.path.join(base_dir, "expected", file_name)


class ParametersTest(unittest.TestCase):

    def setUp(self):
        self.params = Parameters(get_orig_params_path("test_params.json"))
        self.params_exp = Parameters(get_exp_params_path("test_params.json"))

    def tearDown(self):
        del self.params

    # @unittest.skip("skip")
    def test_load_from_json(self):
        self.assertEqual(self.params.__dict__, self.params_exp.__dict__)

    def test_load_from_dict(self):
        with open(get_orig_params_path("test_params.json")) as f:
            params_dict = json.load(f)
        params = Parameters(params_dict)
        self.assertEqual(params.__dict__, self.params_exp.__dict__)

    def test_load_from_parameters_object(self):
        params = Parameters(self.params)
        self.assertEqual(params.__dict__, self.params_exp.__dict__)

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

    def test_get_series_params(self):
        params = Parameters(get_orig_params_path(
            "test_params_time_multicolumn.json"))

        self.assertEqual(params[0]["time_header_coord"], ["A1", "A2"])


if __name__ == '__main__':
    nose.run(defaultTest=__name__)
