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
from xlseries.utils import get_dataframe, infer_freq


class UtilsTest(unittest.TestCase):

    def test_infer_freq(self):

        freq_exp = "M"
        freq = infer_freq(2618767)
        self.assertEqual(freq, freq_exp)

    def test_get_dataframe(self):

        base_dir = os.path.join(os.path.dirname(__file__), "cases")
        path = os.path.join(base_dir, "case1_df.xlsx")
        df = get_dataframe(path)

        self.assertEqual(type(df), pd.DataFrame)

if __name__ == '__main__':
    # nose.main()
    nose.run(defaultTest=__name__)
