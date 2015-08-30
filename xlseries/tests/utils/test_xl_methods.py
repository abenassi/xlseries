#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_xl_methods

Tests for `xl_methods` utils module.
"""

import unittest
import nose
import os
from openpyxl import load_workbook

from xlseries.utils.xl_methods import xl_coordinates_range
from xlseries.utils.xl_methods import make_wb_copy, compare_cells
from xlseries.utils.xl_methods import make_ws_copy, compare_cells_ws
from xlseries.utils.xl_methods import open_xls_as_xlsx
from xlseries.utils.xl_methods import common_row_or_column, coord_in_scope
from xlseries.utils.case_loaders import load_original_case
from xlseries.utils.path_finders import abs_path


class XlMethodsTest(unittest.TestCase):

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

    def test_make_wb_copy(self):
        wb = load_original_case(2)
        wb_copy = make_wb_copy(wb)
        self.assertTrue(compare_cells(wb, wb_copy))

    def test_make_ws_copy(self):
        wb = load_original_case(2)
        ws = wb.active
        ws_copy = make_ws_copy(ws)
        self.assertTrue(compare_cells_ws(ws, ws_copy))

    def test_open_xls_as_xlsx(self):
        wb_xls = open_xls_as_xlsx(abs_path("sh_ipcnu.xls"))
        wb_exp = load_workbook(
            os.path.join(abs_path("expected"), "sh_ipcnu.xlsx"),
            data_only=True)

        self.assertTrue(compare_cells(wb_xls, wb_exp))

    def test_common_row_or_column(self):

        coords = ["A1", "A2", "A3"]
        exp_order = 1
        self.assertEqual(common_row_or_column(coords), exp_order)

        coords = ["A1", "B1", "C1"]
        exp_order = 1
        self.assertEqual(common_row_or_column(coords), exp_order)

        coords = ["A1", "A2", "B3"]
        with self.assertRaises(Exception):
            common_row_or_column(coords)

    def test_coord_in_scope(self):

        coord = "B2"
        coords = ["A1", "A2", "A3"]
        self.assertTrue(coord_in_scope(coord, coords))

        coord = "B2"
        coords = ["B1", "B2", "B3"]
        self.assertTrue(coord_in_scope(coord, coords))

        coord = "B2"
        coords = ["C1", "C2", "C3"]
        self.assertFalse(coord_in_scope(coord, coords))

        coord = "B4"
        coords = ["A1", "A2", "A3"]
        self.assertFalse(coord_in_scope(coord, coords))


if __name__ == '__main__':
    # nose.main()
    nose.run(defaultTest=__name__)
