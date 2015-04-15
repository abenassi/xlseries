#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_xlseries
----------------------------------

Tests for `xlseries` module.
"""

import unittest
import nose
import os
from xlseries.utils.data_frame import get_data_frames
from xlseries.xlseries import XlSeries
from xlseries.utils.data_frame import compare_data_frames


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

@unittest.skip("skip")
class TestXlseries(unittest.TestCase):

    # @load_data_frames("cases")
    def test_case1(self, test_dfs, exp_dfs):
        for test_df, exp_df in zip(test_dfs, exp_dfs):
            self.assertTrue(compare_data_frames(test_df, exp_df))

    # @load_data_frames("cases")
    # @unittest.skip("skip")
    def test_case2(self, test_dfs, exp_dfs):
        # TODO: rework get_data_frames to deal with missing days
        for test_df, exp_df in zip(test_dfs, exp_dfs):
            self.assertTrue(compare_data_frames(test_df, exp_df))

    # @load_data_frames("cases")
    # @unittest.skip("skip")
    def test_case3(self, test_dfs, exp_dfs):
        for test_df, exp_df in zip(test_dfs, exp_dfs):
            self.assertTrue(compare_data_frames(test_df, exp_df))

    # @load_data_frames("cases")
    # @unittest.skip("skip")
    def test_case4(self, test_dfs, exp_dfs):
        for test_df, exp_df in zip(test_dfs, exp_dfs):
            self.assertTrue(compare_data_frames(test_df, exp_df))

    # @load_data_frames("cases")
    # @unittest.skip("skip")
    def test_case5(self, test_dfs, exp_dfs):
        for test_df, exp_df in zip(test_dfs, exp_dfs):
            self.assertTrue(compare_data_frames(test_df, exp_df))

    # @load_data_frames("cases")
    # @unittest.skip("skip")
    def test_case6(self, test_dfs, exp_dfs):
        for test_df, exp_df in zip(test_dfs, exp_dfs):
            self.assertTrue(compare_data_frames(test_df, exp_df))

    # @load_data_frames("cases")
    # @unittest.skip("skip")
    def test_case7(self, test_dfs, exp_dfs):
        for test_df, exp_df in zip(test_dfs, exp_dfs):
            self.assertTrue(compare_data_frames(test_df, exp_df))


if __name__ == '__main__':
    nose.run(defaultTest=__name__)
