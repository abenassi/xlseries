#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_clean_ti_strategies
----------------------------------

Tests for `clean_ti_strategies` module.
"""

import unittest
import nose
import datetime
from openpyxl import load_workbook
import json

from xlseries.strategies.clean.time_index import CleanSimpleTi, CleanComposedTi
from xlseries.utils.general import compare_cells, load_json_vals


# @unittest.skip("skip")
class CleanSimpleTiTestCase(unittest.TestCase):

    def setUp(self):
        self.strategy = CleanSimpleTi

    def test_correct_progression(self):

        last_time_value = datetime.datetime(2011, 7, 5)
        curr_time_value = datetime.datetime(2011, 5, 6)
        freq = "D"
        missings = True
        missing_value = "Implicit"

        new_time_value = self.strategy._correct_progression(last_time_value,
                                                            curr_time_value,
                                                            freq, missings,
                                                            missing_value)
        exp_time_value = datetime.datetime(2011, 7, 6)

        self.assertEqual(new_time_value, exp_time_value)

    def test_parse_time(self):

        value = "17-12.09"
        time_format = datetime.datetime

        new_time_value = self.strategy._parse_time(value, time_format)
        exp_time_value = datetime.datetime(2009, 12, 17)

        self.assertEqual(new_time_value, exp_time_value)

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
                    "missing_value": "Implicit"}

        self.strategy._clean_time_index(ws, clean_ci)

        wb_exp = load_workbook("expected/test_case2.xlsx")

        # wb.save("test_case2_after_cleaning_index.xlsx")
        self.assertTrue(compare_cells(wb, wb_exp))


def parse_t_name(fn_name):
    """Parse the test name from a function name."""
    return "test_" + fn_name.split("_")[-1]


def load_case_name(fn_name_parser, kw_arg):
    """Call a test loading the name of the case.

    Args:
        fn_name_parser: Function to parse the case name from test fn name.
        kw_arg: Name of the parameter to pass case name.
    """

    def test_decorator(fn):
        def test_decorated(*args, **kwargs):
            kwargs[kw_arg] = fn_name_parser(fn.__name__)
            fn(*args, **kwargs)

        test_decorated.__name__ = fn.__name__
        return test_decorated
    return test_decorator


class CleanComposedTiTest(unittest.TestCase):

    def setUp(self):
        self.strategy = CleanComposedTi

    def parse_time_values(self, values):

        time_format = str
        last_time = None

        new_values = []
        for value in values:
            new_values.append(self.strategy._parse_time(value, time_format,
                                                        last_time))

        return new_values

    @load_json_vals("original/", parse_t_name, "values", "parse_time")
    @load_json_vals("expected/", parse_t_name, "exp_vals", "parse_time", True)
    @load_case_name(parse_t_name, "case")
    def test_parse_time_case3(self, case, values, exp_vals):
        """Parse a list of time values using _parse_time method."""

        new_values = self.parse_time_values(values)

        msg = " ".join([str(case), ":", str(new_values),
                        "are not equal to", str(exp_vals)])
        assert new_values == exp_vals, msg

    @load_json_vals("original/", parse_t_name, "values", "parse_time")
    @load_json_vals("expected/", parse_t_name, "exp_vals", "parse_time", True)
    @load_case_name(parse_t_name, "case")
    def test_parse_time_case4(self, case, values, exp_vals):
        """Parse a list of time values using _parse_time method."""

        new_values = self.parse_time_values(values)

        msg = " ".join([str(case), ":", str(new_values),
                        "are not equal to", str(exp_vals)])
        assert new_values == exp_vals, msg

    @load_json_vals("original/", parse_t_name, "values", "parse_time")
    @load_json_vals("expected/", parse_t_name, "exp_vals", "parse_time", True)
    @load_case_name(parse_t_name, "case")
    def test_parse_time_case5(self, case, values, exp_vals):
        """Parse a list of time values using _parse_time method."""

        new_values = self.parse_time_values(values)

        msg = " ".join([str(case), ":", str(new_values),
                        "are not equal to", str(exp_vals)])
        assert new_values == exp_vals, msg

    @load_json_vals("original/", parse_t_name, "values", "parse_time")
    @load_json_vals("expected/", parse_t_name, "exp_vals", "parse_time", True)
    @load_case_name(parse_t_name, "case")
    def test_parse_time_case5b(self, case, values, exp_vals):
        """Parse a list of time values using _parse_time method."""

        new_values = self.parse_time_values(values)

        msg = " ".join([str(case), ":", str(new_values),
                        "are not equal to", str(exp_vals)])
        assert new_values == exp_vals, msg

    @load_json_vals("original/", parse_t_name, "values", "parse_time")
    @load_json_vals("expected/", parse_t_name, "exp_vals", "parse_time", True)
    @load_case_name(parse_t_name, "case")
    def test_parse_time_case6(self, case, values, exp_vals):
        """Parse a list of time values using _parse_time method."""

        new_values = self.parse_time_values(values)

        msg = " ".join([str(case), ":", str(new_values),
                        "are not equal to", str(exp_vals)])
        assert new_values == exp_vals, msg

    @load_json_vals("original/", parse_t_name, "values", "parse_time")
    @load_json_vals("expected/", parse_t_name, "exp_vals", "parse_time", True)
    @load_case_name(parse_t_name, "case")
    def test_parse_time_case6b(self, case, values, exp_vals):
        """Parse a list of time values using _parse_time method."""

        new_values = self.parse_time_values(values)

        msg = " ".join([str(case), ":", str(new_values),
                        "are not equal to", str(exp_vals)])
        assert new_values == exp_vals, msg

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
