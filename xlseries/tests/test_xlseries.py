#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_xlseries

Tests for `xlseries` module.
"""

import unittest
import nose
from functools import wraps

from xlseries.utils.path_finders import get_orig_cases_path
from xlseries.utils.case_loaders import load_original_case
from xlseries.utils.case_loaders import load_expected_case
from xlseries.utils.case_loaders import load_parameters_case
from xlseries.xlseries import XlSeries
from xlseries.utils.data_frame import compare_data_frames


def load_case_number():
    """Decorate a test loading the case number taken from test name."""

    def fn_decorator(fn):
        case_num = int(fn.__name__.split("_")[-1][-1])

        @wraps(fn)
        def fn_decorated(*args, **kwargs):
            kwargs["case_num"] = case_num
            fn(*args, **kwargs)

        return fn_decorated
    return fn_decorator


# @unittest.skip("skip")
class TestXlSeriesWithAllParameters(unittest.TestCase):

    def run_case_with_parameters(self, case_num, specific_params=None,
                                 special_case=None):
        """Run a test case with parameters using ParameterDiscovery strategy.

        Args:
            case_num (int): The test case number to run.
        """
        test_wb = load_original_case(case_num)
        params = load_parameters_case(case_num)
        params["data_ends"] = None
        exp_dfs = load_expected_case(case_num, special_case)

        if specific_params:
            for specific_param, value in specific_params.items():
                params[specific_param] = value

        # get dfs from the strategy
        series = XlSeries(test_wb)
        test_dfs = series.get_data_frames(params)

        if not isinstance(test_dfs, list):
            test_dfs = [test_dfs]
        if not isinstance(exp_dfs, list):
            exp_dfs = [exp_dfs]

        for test_df, exp_df in zip(
            sorted(test_dfs, key=lambda x: len(x) + len(x.index)),
            sorted(exp_dfs, key=lambda x: len(x) + len(x.index))
        ):
            print(test_df.columns, exp_df.columns)
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
        special_case = None
        special_case = "_without_end"
        self.run_case_with_parameters(case_num, special_case=special_case)

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

    def run_case_without_some_parameters(self, case_num, specific_params=None,
                                         special_case=None):
        """Run a test case deleting some parameters.

        Args:
            case_num: The test case number to run.
        """
        test_wb = get_orig_cases_path(case_num)
        params = load_parameters_case(case_num)
        exp_dfs = load_expected_case(case_num, special_case)

        params.remove_non_critical()
        if specific_params:
            for specific_param, value in specific_params.items():
                params[specific_param] = value

        # change safe_mode to True, for complete test in safe_mode (very slow)
        safe_mode = False
        series = XlSeries(test_wb)
        test_dfs = series.get_data_frames(params, safe_mode=safe_mode)

        # get them always into a list
        if not isinstance(test_dfs, list):
            test_dfs = [test_dfs]
        if not isinstance(exp_dfs, list):
            exp_dfs = [exp_dfs]

        for test_df, exp_df in zip(
            sorted(test_dfs, key=lambda x: len(x) + len(x.index)),
            sorted(exp_dfs, key=lambda x: len(x) + len(x.index))
        ):
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
        self.run_case_without_some_parameters(
            case_num, specific_params={"missing_value": u'\u2026'})

    # @unittest.skip("skip")
    @load_case_number()
    def test_case5(self, case_num):
        special_case = None
        special_case = "_without_end"
        self.run_case_without_some_parameters(
            case_num, special_case=special_case)

    # @unittest.skip("skip")
    @load_case_number()
    def test_case6(self, case_num):
        self.run_case_without_some_parameters(
            case_num, specific_params={
                "continuity": False,
                "blank_rows": True
            })

    # @unittest.skip("skip")
    @load_case_number()
    def test_case7(self, case_num):
        self.run_case_without_some_parameters(case_num)


# @unittest.skip("skip")
class TestXlSeriesVariations(TestXlSeriesWithAllParameters):

    # @unittest.skip("skip")
    @load_case_number()
    def test_context_case6(self, case_num):
        specific_params = {"context": {
            "VABpb": "A8-A23",
            "PIBpm": "A8-A27"
        }}
        self.run_case_with_parameters(case_num,
                                      specific_params=specific_params,
                                      special_case="_context")

    @load_case_number()
    def test_composed_header_case6(self, case_num):
        specific_params = {
            "context": {
                "VABpb": "B8-B23",
                "PIBpm": "B8-B27"
            },
            "headers_coord": "(A8_B8)-(A28_B28)"
        }
        self.run_case_with_parameters(case_num,
                                      specific_params=specific_params,
                                      special_case="_composed_headers")


if __name__ == '__main__':
    nose.run(defaultTest=__name__)
