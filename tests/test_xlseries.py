#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_xlseries
----------------------------------

Tests for `xlseries` module.
"""

import unittest
import os
from xlseries.utils import get_dataframe
from pandas.util.testing import assert_frame_equal
from xlseries import xlseries


def load_data_frame(path):
    """Call test with a data frame loaded from case xl file.

    Args:
        path: Relative path where the df xl file is located."""

    def test_decorator(fn):
        base_path = os.path.join(os.path.dirname(__file__), path)
        file_name = fn.__name__ + "_df.xlsx"
        file_path = os.path.join(base_path, file_name)

        df = get_dataframe(file_path)

        def test_decorated(self):
            fn(self, df)

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
        # TODO: add more comparing criteria!!!
        assert_frame_equal(df1, df2)
        return True

    except:
        return False


class TestXlseries(unittest.TestCase):

    @load_data_frame("cases")
    def test_case1(self, df):

        df2 = get_dataframe(
            r"C:\Users\Beni\Documents\Projects\xlseries\tests\cases\test_case1_df.xlsx")
        self.assertTrue(compare_data_frames(df, df2))

    def test_case2(self):
        pass

    def test_case3(self):
        pass

    def test_case4(self):
        pass

    def test_case5(self):
        pass

    def test_case6(self):
        pass

    def test_case7(self):
        pass

    def test_case8(self):
        pass


if __name__ == '__main__':
    unittest.main()
