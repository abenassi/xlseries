#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_data_frame

Tests for `data_frame` utils module.
"""

import unittest
import nose
import os
import pandas as pd
import datetime

from xlseries.utils.data_frame import get_data_frame, compare_period_ranges
from xlseries.utils.data_frame import get_data_frames, dfs_to_json_and_csv
from xlseries.utils.data_frame import compare_data_frames
from xlseries.utils.case_loaders import load_expected_case


class XlMethodsTest(unittest.TestCase):

    def check_get_data_frames(self, case_num, func, file_format, directory):
        """Test functions to get data frames from files.

        Check that the object returned by func is a pandas data frame.

        Args:
            case_num (int): Number of test case.
            func (func): Function to be used to load a data frame from a file.
            file_format (str): Format of the file with a serialized data frame
                (can be csv, json or xlsx)
            dir (str): Folder where files with serialized data frames are.
        """

        base_dir = os.path.join(os.path.dirname(__file__), directory)
        path = os.path.join(base_dir, "test_case" + str(case_num) +
                            "." + file_format)
        dfs = func(path)

        if isinstance(dfs, list):
            for df in dfs:
                self.assertEqual(type(df), pd.DataFrame)
        else:
            self.assertEqual(type(dfs), pd.DataFrame)

    def test_get_data_frame(self):
        """Test getting a serialized data frame."""
        self.check_get_data_frames(1, get_data_frame, "xlsx", "expected")
        self.check_get_data_frames(1, get_data_frame, "csv", "expected")
        self.check_get_data_frames(1, get_data_frame, "json", "expected")

    def test_get_data_frames(self):
        """Test getting a serialized data frame with a function for many.

        When many dataframes are serialized under the same file name,
        get_data_frames is used."""

        self.check_get_data_frames(1, get_data_frames, "xlsx", "expected")
        self.check_get_data_frames(1, get_data_frames, "csv", "expected")
        self.check_get_data_frames(1, get_data_frames, "json", "expected")

        self.check_get_data_frames(2, get_data_frames, "xlsx", "expected")
        self.check_get_data_frames(2, get_data_frames, "csv", "expected")
        self.check_get_data_frames(2, get_data_frames, "json", "expected")

    def test_compare_period_ranges(self):
        """Test a function to compare period ranges."""

        start = datetime.datetime(2015, 2, 16)
        end = datetime.datetime(2015, 5, 7)

        pr1 = pd.period_range(start, end, freq="D")
        pr2 = pd.period_range(start, periods=81, freq="D")
        pr3 = pd.period_range(end=end, periods=81)
        pr4 = pd.period_range(start, end, freq="M")
        pr5 = pd.period_range(start, end, freq="D", name="my_name")

        self.assertTrue(compare_period_ranges(pr1, pr2))
        self.assertTrue(compare_period_ranges(pr1, pr3))
        self.assertFalse(compare_period_ranges(pr1, pr4))
        self.assertTrue(compare_period_ranges(pr1, pr5))

    def test_compare_data_frames(self):
        """Test a function to compare data frames."""

        df1 = load_expected_case(1)[0]
        df2 = load_expected_case(1)[0]
        df3 = load_expected_case(2)[0]

        self.assertTrue(compare_data_frames(df1, df2))

        with self.assertRaises(AssertionError):
            compare_data_frames(df1, df3)

    def test_dfs_to_json_and_csv(self):
        """Test conversion of xlsx serialized data frames into json and csv."""

        base_dir = os.path.join(os.path.dirname(__file__), "dfs_xlsx")
        dfs_to_json_and_csv(base_dir)

        self.check_get_data_frames(1, get_data_frame, "csv", base_dir)
        self.check_get_data_frames(1, get_data_frame, "json", base_dir)

        os.remove(os.path.join(base_dir, "test_case1.csv"))
        os.remove(os.path.join(base_dir, "test_case1.json"))


if __name__ == '__main__':
    # nose.main()
    nose.run(defaultTest=__name__)
