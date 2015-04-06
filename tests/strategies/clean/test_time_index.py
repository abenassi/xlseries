#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_clean_ti_strategies
----------------------------------

Tests for `clean_ti_strategies` module.
"""

import unittest
import nose
import arrow
import datetime
from openpyxl import load_workbook
import os

from xlseries.strategies.clean.time_index import CleanSingleColumnTi
from xlseries.utils.general import get_package_dir
from xlseries.strategies.discover.parameters import Parameters
from xlseries.utils.general import compare_cells


def load_parameters(case):

    base_path = os.path.join(get_package_dir("xlseries", __file__),
                             r"tests\integration_cases\parameters")
    file_name = case + ".json"
    file_path = os.path.join(base_path, file_name)
    params = Parameters(file_path)

    return params


# @unittest.skip("skip")
class CleanSingleColumnTiTest(unittest.TestCase):

    # @unittest.skip("skip")
    def test_correct_progression(self):

        last_time_value = arrow.get(2011, 7, 5)
        curr_time_value = arrow.get(2011, 5, 6)
        freq = "D"
        missings = True
        missing_value = "Implicit"

        new_time_value = CleanSingleColumnTi._correct_progression(
            last_time_value,
            curr_time_value,
            freq, missings,
            missing_value)
        exp_time_value = arrow.get(2011, 7, 6)

        self.assertEqual(new_time_value, exp_time_value)

    # @unittest.skip("skip")
    def test_parse_time(self):

        value = "17-12.09"
        last_time = None

        params = load_parameters("test_case1")
        # print repr(params[0])

        new_time_value = CleanSingleColumnTi._parse_time(value, last_time,
                                                         params[0])
        exp_time_value = arrow.get(2009, 12, 17)

        self.assertEqual(new_time_value, exp_time_value)

    # @unittest.skip("skip")
    def test_clean_time_index(self):

        wb = load_workbook("original/test_case2.xlsx")
        ws = wb.active

        clean_ci = {"time_alignment": 0,
                    "time_format": datetime.datetime,
                    "time_header_coord": "C4",
                    "data_starts": 5,
                    "data_ends": 2993,
                    "frequency": "D",
                    "missings": True,
                    "missing_value": "Implicit",
                    "time_multicolumn": False,
                    "time_composed": False}

        CleanSingleColumnTi._clean_time_index(ws, clean_ci)

        wb_exp = load_workbook("expected/test_case2.xlsx")

        # wb.save("test_case2_after_cleaning_index.xlsx")
        self.assertTrue(compare_cells(wb, wb_exp))


if __name__ == '__main__':
    nose.run(defaultTest=__name__)
