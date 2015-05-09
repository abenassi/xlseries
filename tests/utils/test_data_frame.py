#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_data_frame
----------------------------------

Tests for `data_frame` utils module.
"""

from __future__ import unicode_literals
import unittest
import nose
import os
import pandas as pd
import datetime

from xlseries.utils.data_frame import get_data_frame, compare_period_ranges
from xlseries.utils.data_frame import compare_data_frames
from xlseries.utils.case_loaders import load_expected_case


class XlMethodsTest(unittest.TestCase):

    def test_get_data_frame(self):

        base_dir = os.path.join(os.path.dirname(__file__), "expected/")
        path = os.path.join(base_dir, "test_case1.xlsx")
        df = get_data_frame(path)

        self.assertEqual(type(df), pd.DataFrame)

    def test_get_data_frames(self):
        pass

    def test_compare_period_ranges(self):

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

        df1 = load_expected_case(1)[0]
        df2 = load_expected_case(1)[0]
        df3 = load_expected_case(2)[0]

        self.assertTrue(compare_data_frames(df1, df2))

        with self.assertRaises(AssertionError):
            compare_data_frames(df1, df3)

    def test_dfs_to_json_and_csv(self):
        pass


if __name__ == '__main__':
    # nose.main()
    nose.run(defaultTest=__name__)
