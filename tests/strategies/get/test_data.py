#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_get_data_strategies

Tests for `get_data_strategies` module.
"""

import unittest
import nose

from xlseries.strategies.get.data import GetSingleFrequencyContinuous
from xlseries.strategies.clean.time_index import CleanSingleColumn
from xlseries.utils.comparing import compare_list_values
from xlseries.utils.case_loaders import load_parameters_case
from xlseries.utils.case_loaders import load_original_case
from xlseries.utils.case_loaders import load_expected_case


# @unittest.skip("skip")
class MissingsTestCase(unittest.TestCase):

    def _get_values(self, ws, ini_row, end_row, col):

        values = []
        i_row = ini_row
        while i_row <= end_row:
            values.append(ws.cell(row=i_row, column=col).value)
            i_row += 1

        return values

    def test_fill_implicit_missings(self):
        test_wb = load_original_case(2)
        params = load_parameters_case(2)
        strategy = GetSingleFrequencyContinuous

        ws = test_wb.active

        ini_row = 5
        end_row = 2993
        col = 4

        values = self._get_values(ws, ini_row, end_row, col)
        frequency = "D"
        time_header_coord = "C4"

        CleanSingleColumn().clean_time_index(ws, params[0])

        new_values = strategy._fill_implicit_missings(ws, values, frequency,
                                                      time_header_coord,
                                                      ini_row,
                                                      end_row)

        exp_dfs = load_expected_case(2)
        exp_values = [value[0] for value in exp_dfs[0].values]

        self.assertEqual(len(new_values), len(exp_values))

        self.assertTrue(compare_list_values(new_values, exp_values))


if __name__ == '__main__':
    nose.run(defaultTest=__name__)
