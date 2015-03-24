#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_strategies
----------------------------------

Tests for `strategies` module.
"""

import unittest
import nose
from openpyxl import load_workbook
import pandas as pd

from xlseries.utils.general import get_data_frames, change_working_dir
from xlseries.utils.general import load_file
from xlseries.utils.test import compare_data_frames, compare_period_ranges
from xlseries.strategies.strategies import ParameterDiscovery
from xlseries.parameters import Parameters

REL_WORKING_DIR = r"tests\integration_cases"
PACKAGE_NAME = "xlseries"


def parse_t_name(fn_name):
    """Parse the test name from a function name."""
    return "_".join(fn_name.split("_")[:2])


# @unittest.skip("skip")
class ParameterDiscoveryTestCase(unittest.TestCase):

    @load_file("parameters/", parse_t_name, ".json", Parameters, "params")
    @load_file("expected/", parse_t_name, ".xlsx", get_data_frames, "exp_dfs")
    @load_file("original/", parse_t_name, ".xlsx", load_workbook, "test_wb")
    @change_working_dir(PACKAGE_NAME, REL_WORKING_DIR)
    # @unittest.skip("skip")
    def test_case1_with_params(self, test_wb, exp_dfs, params):
        """Test the strategy with case1 and providing parameters."""

        # get dfs from the strategy
        strategy_obj = ParameterDiscovery(test_wb, params)
        test_dfs = strategy_obj.get_data_frames()

        for test_df, exp_df in zip(test_dfs, exp_dfs):
            self.assertTrue(compare_data_frames(test_df, exp_df))

    @load_file("parameters/", parse_t_name, ".json", Parameters, "params")
    @load_file("expected/", parse_t_name, ".xlsx", get_data_frames, "exp_dfs")
    @load_file("original/", parse_t_name, ".xlsx", load_workbook, "test_wb")
    @change_working_dir(PACKAGE_NAME, REL_WORKING_DIR)
    # @unittest.skip("skip")
    def test_case2_with_params(self, test_wb, exp_dfs, params):
        """Test the strategy with case2 and providing parameters."""

        # get dfs from the strategy
        strategy_obj = ParameterDiscovery(test_wb, params)
        test_dfs = strategy_obj.get_data_frames()

        for test_df, exp_df in zip(test_dfs, exp_dfs):

            msg = "Different index size: " + str(test_df.index.size) + \
                "  " + str(exp_df.index.size)
            assert test_df.index.size == exp_df.index.size, msg

            self.assertTrue(compare_data_frames(test_df, exp_df))

    @load_file("parameters/", parse_t_name, ".json", Parameters, "params")
    @load_file("expected/", parse_t_name, ".xlsx", get_data_frames, "exp_dfs")
    @load_file("original/", parse_t_name, ".xlsx", load_workbook, "test_wb")
    @change_working_dir(PACKAGE_NAME, REL_WORKING_DIR)
    @unittest.skip("skip")
    def test_case3_with_params(self, test_wb, exp_dfs, params):
        """Test the strategy with case3 and providing parameters."""

        # get dfs from the strategy
        strategy_obj = ParameterDiscovery(test_wb, params)
        test_dfs = strategy_obj.get_data_frames()

        for test_df, exp_df in zip(test_dfs, exp_dfs):
            self.assertTrue(compare_data_frames(test_df, exp_df))


# @unittest.skip("skip")
class PeriodRangeTestCase(unittest.TestCase):

    @change_working_dir(PACKAGE_NAME, REL_WORKING_DIR)
    def test_get_period_ranges(self):

        test_wb = load_workbook("original/test_case2.xlsx")
        params = Parameters("parameters/test_case2.json")
        strategy_obj = ParameterDiscovery(test_wb, params)
        ws = strategy_obj.wb.active

        pr_d = pd.period_range("20020304", "20140410", freq="D")
        pr_m = pd.period_range("20020301", "20130301", freq="M")

        period_ranges = strategy_obj._get_period_ranges(ws)

        self.assertTrue(compare_period_ranges(pr_d, period_ranges[0]))
        self.assertTrue(compare_period_ranges(pr_m, period_ranges[1]))


if __name__ == '__main__':
    nose.run(defaultTest=__name__)
