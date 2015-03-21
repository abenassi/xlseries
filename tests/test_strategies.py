#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_strategies
----------------------------------

Tests for `strategies` module.
"""
import sys
import unittest
import nose
import os
from openpyxl import load_workbook
import datetime
import pandas as pd

from xlseries.utils import get_data_frames, approx_equal, compare_cells
from xlseries import XlSeries
from utils import compare_data_frames, compare_period_ranges
from utils import compare_list_values
from xlseries.strategies import ParameterDiscovery
from xlseries.parameters import Parameters


def load_wb_and_data_frame(path):
    """Call test with a test workbook and expected data frame.

    Args:
        path: Relative path where the df xl file is located."""

    def test_decorator(fn):

        base_path = os.path.join(os.path.dirname(__file__), path)

        # load expected data frame
        exp_file_name = parse_t_name(fn.__name__) + "_exp.xlsx"
        exp_file_path = os.path.join(base_path, exp_file_name)
        exp_dfs = get_data_frames(exp_file_path)

        # get result data frame from xlseries for the test xl file
        test_file_name = parse_t_name(fn.__name__) + ".xlsx"
        test_file_path = os.path.join(base_path, test_file_name)
        test_wb = load_workbook(test_file_path)

        def test_decorated(self):
            fn(self, test_wb=test_wb, exp_dfs=exp_dfs)

        test_decorated.__name__ = fn.__name__
        return test_decorated
    return test_decorator


def load_params(path):
    """Load parameters in a test case.

    Args:
        path: Relative path where the params json file is located."""

    def test_decorator(fn):

        base_path = os.path.join(os.path.dirname(__file__), path)

        # parse parameters from json file
        params_file_name = parse_t_name(fn.__name__) + "_params.json"
        params_file_path = os.path.join(base_path, params_file_name)
        params = Parameters(params_file_path)

        def test_decorated(self, test_wb, exp_dfs):
            fn(self, test_wb=test_wb, exp_dfs=exp_dfs, params=params)

        test_decorated.__name__ = fn.__name__
        return test_decorated
    return test_decorator


def parse_t_name(fn_name):
    """Parse the test name from a function name."""
    return "_".join(fn_name.split("_")[:2])


# @unittest.skip("skip")
class ParameterDiscoveryTestCase(unittest.TestCase):

    @load_wb_and_data_frame("cases")
    @load_params("cases")
    # @unittest.skip("skip")
    def test_case1_with_params(self, test_wb, exp_dfs, params):
        """Test the strategy with case1 and providing parameters."""

        # get dfs from the strategy
        strategy_obj = ParameterDiscovery(test_wb, params)
        test_dfs = strategy_obj.get_data_frames()

        for test_df, exp_df in zip(test_dfs, exp_dfs):
            self.assertTrue(compare_data_frames(test_df, exp_df))

    @load_wb_and_data_frame("cases")
    @load_params("cases")
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

    # @load_wb_and_data_frame("cases")
    # @load_params("cases")
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

    def test_get_period_ranges(self):

        test_wb = load_workbook("cases/test_case2.xlsx")
        params = Parameters("cases/test_case2_params.json")
        strategy_obj = ParameterDiscovery(test_wb, params)
        ws = strategy_obj.wb.active

        pr_d = pd.period_range("20020304", "20140410", freq="D")
        pr_m = pd.period_range("20020301", "20130301", freq="M")

        period_ranges = strategy_obj._get_period_ranges(ws)
        # print period_ranges

        self.assertTrue(compare_period_ranges(pr_d, period_ranges[0]))
        self.assertTrue(compare_period_ranges(pr_m, period_ranges[1]))


class MissingsTestCase(unittest.TestCase):

    def _get_values(self, ws, ini_row, end_row, col):

        values = []
        i_row = ini_row
        while i_row <= end_row:
            values.append(ws.cell(row=i_row, column=col).value)
            i_row += 1

        return values

    def test_fill_implicit_missings(self):
        test_wb = load_workbook("cases/test_case2.xlsx")
        params = Parameters("cases/test_case2_params.json")
        pd = ParameterDiscovery

        ws = test_wb.active
        ini_row = 5
        end_row = 2993
        col = 4

        values = self._get_values(ws, ini_row, end_row, col)
        frequency = "D"
        time_header_coord = "C4"

        pd._clean_time_index(ws,
                             params.time_alignment[0],
                             params.time_format[0],
                             params.time_header_coord[0],
                             params.data_starts[0],
                             params.data_ends[0],
                             params.frequency[0],
                             params.missings[0],
                             params.missing_value[0])

        new_values = pd._fill_implicit_missings(ws, values, frequency,
                                                time_header_coord, ini_row,
                                                end_row)

        exp_dfs = get_data_frames("cases/test_case2_exp.xlsx")
        exp_values = [value[0] for value in exp_dfs[0].values]

        self.assertEqual(len(new_values), len(exp_values))

        with open("record.txt", "wb") as f:
            for value1, value2 in zip(new_values, exp_values):
                f.write(str(value1).ljust(20) + str(value2).ljust(20) +
                        str(approx_equal(value1, value2, 0.001)).ljust(20) + "\n")

        self.assertTrue(compare_list_values(new_values, exp_values))


class TimeTestCase(unittest.TestCase):

    def setUp(self):
        self.pd = ParameterDiscovery

    def test_increment_time(self):
        time = datetime.datetime(2015, 12, 1)

        new_time = self.pd._increment_time(time, 1, "S")
        exp_new_time = datetime.datetime(2015, 12, 1, 0, 0, 1)
        self.assertEqual(new_time, exp_new_time)

        new_time = self.pd._increment_time(time, 1, "D")
        exp_new_time = datetime.datetime(2015, 12, 2)
        self.assertEqual(new_time, exp_new_time)

        new_time = self.pd._increment_time(time, 1, "M")
        exp_new_time = datetime.datetime(2016, 1, 1)
        self.assertEqual(new_time, exp_new_time)

        new_time = self.pd._increment_time(time, 1, "Q")
        exp_new_time = datetime.datetime(2016, 3, 1)
        self.assertEqual(new_time, exp_new_time)

        new_time = self.pd._increment_time(time, 1, "Y")
        exp_new_time = datetime.datetime(2016, 12, 1)
        self.assertEqual(new_time, exp_new_time)

    def test_correct_progression(self):

        last_time_value = datetime.datetime(2011, 7, 5)
        curr_time_value = datetime.datetime(2011, 5, 6)
        freq = "D"
        missings = True
        missing_value = "Implicit"

        new_time_value = self.pd._correct_progression(last_time_value,
                                                      curr_time_value,
                                                      freq, missings,
                                                      missing_value)
        exp_time_value = datetime.datetime(2011, 7, 6)

        self.assertEqual(new_time_value, exp_time_value)

    def test_parse_time(self):

        value = "17-12.09"
        time_format = datetime.datetime

        new_time_value = self.pd._parse_time(value, time_format)
        exp_time_value = datetime.datetime(2009, 12, 17)

        self.assertEqual(new_time_value, exp_time_value)

    def test_clean_time_index(self):

        wb = load_workbook("cases/test_case2.xlsx")
        ws = wb.active

        time_alignment = 0
        time_format = datetime.datetime
        time_header_coord = "C4"
        ini_row = 5
        end_row = 2993
        freq = "D"
        miss_presence = True
        missing_value = "Implicit"

        self.pd._clean_time_index(ws, time_alignment, time_format,
                                  time_header_coord, ini_row, end_row,
                                  freq, miss_presence, missing_value)

        wb_exp = load_workbook("cases/test_case2_clean_index.xlsx")

        wb.save("test_case2_after_cleaning_index.xlsx")
        self.assertTrue(compare_cells(wb, wb_exp))

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
