#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_xlseries

Tests for `xlseries` module.
"""

import unittest
import nose
import os
from functools import wraps

from xlseries.utils.path_finders import get_orig_cases_path
from xlseries.utils.path_finders import get_param_cases_path
from xlseries.utils.case_loaders import load_expected_case
from xlseries.utils.case_loaders import load_parameters_case
from xlseries.xlseries import XlSeries
from xlseries.utils.data_frame import compare_data_frames


def load_case_number():
    """Decorate a test loading the case number taken from test name."""

    def fn_decorator(fn):
        case_num = int(fn.__name__.split("_")[1][-1])

        @wraps(fn)
        def fn_decorated(*args, **kwargs):
            kwargs["case_num"] = case_num
            fn(*args, **kwargs)

        return fn_decorated
    return fn_decorator


# @unittest.skip("skip")
class TestXlSeriesWithAllParameters(unittest.TestCase):

    def run_case_with_parameters(self, case_num):
        """Run a test case with parameters using ParameterDiscovery strategy.

        Args:
            case_num: The test case number to run.
        """
        test_wb = get_orig_cases_path(case_num)
        params = get_param_cases_path(case_num)
        exp_dfs = load_expected_case(case_num)

        # get dfs from the strategy
        series = XlSeries(test_wb)
        test_dfs = series.get_data_frames(params)

        for test_df, exp_df in zip(test_dfs, exp_dfs):
            print test_df.columns, exp_df.columns
            self.assertTrue(compare_data_frames(test_df, exp_df))

    # @unittest.skip("skip")
    @load_case_number()
    def test_case1(self, case_num):
        self.run_case_with_parameters(case_num)

    # @unittest.skip("skip")
    @load_case_number()
    def test_case2(self, case_num):
        self.run_case_with_parameters(case_num)

    # @unittest.skip("skip")
    @load_case_number()
    def test_case3(self, case_num):
        self.run_case_with_parameters(case_num)

    # @unittest.skip("skip")
    @load_case_number()
    def test_case4(self, case_num):
        self.run_case_with_parameters(case_num)

    # @unittest.skip("skip")
    @load_case_number()
    def test_case5(self, case_num):
        self.run_case_with_parameters(case_num)

    # @unittest.skip("skip")
    @load_case_number()
    def test_case6(self, case_num):
        self.run_case_with_parameters(case_num)

    # @unittest.skip("skip")
    @load_case_number()
    def test_case7(self, case_num):
        self.run_case_with_parameters(case_num)


# @unittest.skip("skip")
class TestXlSeriesWithoutSomeParameters(unittest.TestCase):

    def run_case_without_some_parameters(self, case_num, specific_params=None):
        """Run a test case deleting some parameters.

        Args:
            case_num: The test case number to run.
        """
        test_wb = get_orig_cases_path(case_num)
        params = load_parameters_case(case_num)
        exp_dfs = load_expected_case(case_num)

        params.remove_non_critical()
        if specific_params:
            for specific_param, value in specific_params.iteritems():
                params[specific_param] = value

        # test not in safe mode
        series = XlSeries(test_wb)
        test_dfs = series.get_data_frames(params, False)

        for test_df, exp_df in zip(test_dfs, exp_dfs):
            self.assertTrue(compare_data_frames(test_df, exp_df))

    # @unittest.skip("skip")
    @load_case_number()
    def test_case1(self, case_num):
        self.run_case_without_some_parameters(case_num)

    # @unittest.skip("skip")
    @load_case_number()
    def test_case2(self, case_num):
        self.run_case_without_some_parameters(case_num)

    # @unittest.skip("skip")
    @load_case_number()
    def test_case3(self, case_num):
        self.run_case_without_some_parameters(case_num)

    # @unittest.skip("skip")
    @load_case_number()
    def test_case4(self, case_num):
        specific_params = {"missing_value": u'\u2026'}
        self.run_case_without_some_parameters(case_num, specific_params)

    # @unittest.skip("skip")
    @load_case_number()
    def test_case5(self, case_num):
        self.run_case_without_some_parameters(case_num)

    # @unittest.skip("skip")
    @load_case_number()
    def test_case6(self, case_num):
        self.run_case_without_some_parameters(case_num)

    # @unittest.skip("skip")
    @load_case_number()
    def test_case7(self, case_num):
        self.run_case_without_some_parameters(case_num)


if __name__ == '__main__':
    nose.run(defaultTest=__name__)
