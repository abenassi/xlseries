#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_xlseries
----------------------------------

Tests for `xlseries` module.
"""

import unittest
import os
from xlseries.utils import get_data_frames
from pandas.util.testing import assert_frame_equal
from xlseries import XlSeries


def load_data_frames(path):
    """Call test with a data frame loaded from case xl file.

    Args:
        path: Relative path where the df xl file is located."""

    def test_decorator(fn):

        base_path = os.path.join(os.path.dirname(__file__), path)

        # load expected data frame
        exp_file_name = fn.__name__ + "_exp.xlsx"
        exp_file_path = os.path.join(base_path, exp_file_name)
        exp_dfs = get_data_frames(exp_file_path)

        # get result data frame from xlseries for the test xl file
        test_file_name = fn.__name__ + ".xlsx"
        test_file_path = os.path.join(base_path, test_file_name)
        xl_series = XlSeries(test_file_path)
        test_dfs = xl_series.get_data_frames()
        # test_dfs = exp_dfs

        def test_decorated(self):
            fn(self, test_dfs, exp_dfs)

        return test_decorated
    return test_decorator


def compare_data_frames(df1, df2):
    """Wrapper to compare two data frames using assert_frame_equal.

    Args:
        df1: First data frame to compare.
        df2: Second data frame to compare.
    """

    try:
        # returns None when data frames are equal
        assert_frame_equal(df1, df2,
                           check_dtype=True,
                           check_index_type=True,
                           check_column_type=True,
                           check_frame_type=True,
                           check_less_precise=True,
                           check_names=True,
                           by_blocks=True,
                           check_exact=True)
        return True

    except:
        return False


class TestXlseries(unittest.TestCase):

    @load_data_frames("cases")
    def test_case1(self, test_dfs, exp_dfs):
        for test_df, exp_df in zip(test_dfs, exp_dfs):
            self.assertTrue(compare_data_frames(test_df, exp_df))

    @load_data_frames("cases")
    # @unittest.skip("skip")
    def test_case2(self, test_dfs, exp_dfs):
        # TODO: rework get_data_frames to deal with missing days
        for test_df, exp_df in zip(test_dfs, exp_dfs):
            self.assertTrue(compare_data_frames(test_df, exp_df))

    @load_data_frames("cases")
    # @unittest.skip("skip")
    def test_case3(self, test_dfs, exp_dfs):
        for test_df, exp_df in zip(test_dfs, exp_dfs):
            self.assertTrue(compare_data_frames(test_df, exp_df))

    @load_data_frames("cases")
    # @unittest.skip("skip")
    def test_case4(self, test_dfs, exp_dfs):
        for test_df, exp_df in zip(test_dfs, exp_dfs):
            self.assertTrue(compare_data_frames(test_df, exp_df))

    @load_data_frames("cases")
    # @unittest.skip("skip")
    def test_case5(self, test_dfs, exp_dfs):
        for test_df, exp_df in zip(test_dfs, exp_dfs):
            self.assertTrue(compare_data_frames(test_df, exp_df))

    @load_data_frames("cases")
    # @unittest.skip("skip")
    def test_case6(self, test_dfs, exp_dfs):
        for test_df, exp_df in zip(test_dfs, exp_dfs):
            self.assertTrue(compare_data_frames(test_df, exp_df))

    @load_data_frames("cases")
    # @unittest.skip("skip")
    def test_case7(self, test_dfs, exp_dfs):
        for test_df, exp_df in zip(test_dfs, exp_dfs):
            self.assertTrue(compare_data_frames(test_df, exp_df))


if __name__ == '__main__':
    unittest.main()
