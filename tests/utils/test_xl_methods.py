#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_xl_methods

Tests for `xl_methods` utils module.
"""

import unittest
import nose
from xlseries.utils.xl_methods import xl_coordinates_range
from xlseries.utils.xl_methods import make_wb_copy, compare_cells
from xlseries.utils.case_loaders import load_original_case


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


if __name__ == '__main__':
    # nose.main()
    nose.run(defaultTest=__name__)
