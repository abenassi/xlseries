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
from xlseries.utils.data_frame import get_data_frame


class XlMethodsTest(unittest.TestCase):

    def test_get_dataframe(self):

        base_dir = os.path.join(os.path.dirname(__file__), "expected/")
        path = os.path.join(base_dir, "test_case1.xlsx")
        df = get_data_frame(path)

        self.assertEqual(type(df), pd.DataFrame)


if __name__ == '__main__':
    # nose.main()
    nose.run(defaultTest=__name__)
