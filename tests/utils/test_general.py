#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_utils
----------------------------------

Tests for `utils` module.
"""

import unittest
import nose
import os
import pandas as pd
from xlseries.utils.general import get_data_frame, infer_freq
from xlseries.utils.general import load_file
from xlseries.utils.general import xl_coordinates_range


class UtilsTest(unittest.TestCase):

    def test_infer_freq(self):

        freq_exp = "M"
        freq = infer_freq(2618767)
        self.assertEqual(freq, freq_exp)

    def test_get_dataframe(self):

        base_dir = os.path.join(os.path.dirname(__file__), "expected/")
        path = os.path.join(base_dir, "test_case1.xlsx")
        df = get_data_frame(path)

        self.assertEqual(type(df), pd.DataFrame)

    def test_xl_coordinates_range(self):

        obs = list(xl_coordinates_range("A5", "A7"))
        exp = ["A5", "A6", "A7"]
        self.assertEqual(obs, exp)

        obs = list(xl_coordinates_range("A5", "C5"))
        exp = ["A5", "B5", "C5"]
        self.assertEqual(obs, exp)

        obs = list(xl_coordinates_range("A5", "C7"))
        exp = ["A5", "B5", "C5",
               "A6", "B6", "C6",
               "A7", "B7", "C7"]
        self.assertEqual(obs, exp)

        obs = list(xl_coordinates_range("A5"))
        exp = ["A5"]
        self.assertEqual(obs, exp)


if __name__ == '__main__':
    # nose.main()
    nose.run(defaultTest=__name__)
