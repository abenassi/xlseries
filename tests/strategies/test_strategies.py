#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_strategies
----------------------------------

Tests for `strategies` module.
"""

from __future__ import unicode_literals
import unittest
import nose
from openpyxl import load_workbook
import pandas as pd
import os
from functools import wraps

from xlseries.utils.general import change_working_dir
from xlseries.utils.case_loaders import load_original_case
from xlseries.utils.case_loaders import load_parameters_case
from xlseries.utils.case_loaders import load_expected_case
from xlseries.utils.test import compare_data_frames, compare_period_ranges
from xlseries.strategies.strategies import ParameterDiscovery
from xlseries.strategies.discover.parameters import Parameters

REL_WORKING_DIR = os.path.join("tests", "integration_cases")
PACKAGE_NAME = "xlseries"


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
class ParameterDiscoveryTestCase(unittest.TestCase):

    def run_case_with_parameters(self, case_num):
        """Run a test case with parameters using ParameterDiscovery strategy.

        Args:
            case_num: The test case number to run.
        """
        test_wb = load_original_case(case_num)
        params = load_parameters_case(case_num)
        exp_dfs = load_expected_case(case_num)

        # get dfs from the strategy
        strategy_obj = ParameterDiscovery(test_wb, params)
        test_dfs = strategy_obj.get_data_frames()

        for test_df, exp_df in zip(test_dfs, exp_dfs):
            self.assertTrue(compare_data_frames(test_df, exp_df))

    @load_case_number()
    # @unittest.skip("skip")
    def test_case1_with_params(self, case_num):
        """Test the strategy with case1 and providing parameters."""
        self.run_case_with_parameters(case_num)

    @load_case_number()
    # @unittest.skip("skip")
    def test_case2_with_params(self, case_num):
        """Test the strategy with case2 and providing parameters."""
        self.run_case_with_parameters(case_num)

    @load_case_number()
    # @unittest.skip("skip")
    def test_case3_with_params(self, case_num):
        """Test the strategy with case3 and providing parameters."""
        self.run_case_with_parameters(case_num)

    @load_case_number()
    @unittest.skip("skip")
    def test_case4_with_params(self, case_num):
        """Test the strategy with case4 and providing parameters."""
        self.run_case_with_parameters(case_num)


# @unittest.skip("skip")
class PeriodRangeTestCase(unittest.TestCase):

    @change_working_dir(PACKAGE_NAME, REL_WORKING_DIR)
    def test_get_period_ranges(self):

        test_wb = load_workbook("original/test_case2.xlsx")
        params = Parameters("parameters/test_case2.json")
        strategy_obj = ParameterDiscovery(test_wb, params)
        ws = strategy_obj.wb.active

        pr_d = pd.period_range("20020304", "20140410", freq="D")
        pr_m = pd.period_range("20020301", "20140301", freq="M")

        period_ranges = strategy_obj._get_period_ranges(ws)

        self.assertTrue(compare_period_ranges(pr_d, period_ranges[0]))
        self.assertTrue(compare_period_ranges(pr_m, period_ranges[1]))


if __name__ == '__main__':
    # unittest.main()
    nose.run(defaultTest=__name__)
