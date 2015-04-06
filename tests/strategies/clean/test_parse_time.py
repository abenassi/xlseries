#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_clean_ti_strategies
----------------------------------

Tests for `clean_ti_strategies` module.
"""
from __future__ import unicode_literals
import unittest
import nose
import arrow
from openpyxl import load_workbook
import json
import os

from xlseries.strategies.clean.parse_time import ParseComposedQuarterTime1
from xlseries.strategies.clean.parse_time import ParseComposedQuarterTime2
from xlseries.strategies.clean.parse_time import ParseComposedMonthTime1
from xlseries.strategies.clean.parse_time import ParseComposedMonthTime2
from xlseries.strategies.clean.parse_time import ParseSimpleTime
from xlseries.utils.general import compare_cells, load_json_vals
from xlseries.strategies.discover.parameters import Parameters
from xlseries.utils.general import change_working_dir
from xlseries.utils.general import load_file, get_package_dir

REL_WORKING_DIR = r"tests\integration_cases"
PACKAGE_NAME = "xlseries"


def load_parameters():
    """Call a test loading the integration test case parameters."""

    def test_decorator(fn):
        base_path = os.path.join(get_package_dir("xlseries", __file__),
                                 r"tests\integration_cases\parameters")
        file_name = parse_t_name_without_bis(fn.__name__) + ".json"
        file_path = os.path.join(base_path, file_name)
        params = Parameters(file_path)

        def test_decorated(*args, **kwargs):
            kwargs["params"] = params
            fn(*args, **kwargs)

        test_decorated.__name__ = fn.__name__
        return test_decorated
    return test_decorator


def parse_t_name(fn_name):
    """Parse the test name from a function name."""
    return "test_" + fn_name.split("_")[-1]


def parse_t_name_without_bis(fn_name):
    """Parse the test name from a function name."""
    if fn_name.split("_")[-1][-1].isdigit():
        return "test_" + fn_name.split("_")[-1]
    else:
        return "test_" + fn_name.split("_")[-1][:-1]


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


class ParseSimpleTimeTest(unittest.TestCase):

    @load_parameters()
    def test_parse_simple_time_case1(self, params):

        value = "17-12.09"
        last_time = None
        # raise Exception(params[0])
        new_value = ParseSimpleTime._parse_time(value, last_time, params[0])

        exp_value = arrow.get(2009, 12, 17)

        self.assertEqual(new_value, exp_value)


class ParseComposedTimeTest(unittest.TestCase):

    def parse_time_values(self, strategy, values, params):

        last_time = None

        new_values = []
        for value in values:
            # print value.encode("utf-8", "ignore")
            new_time = strategy._parse_time(value,
                                            last_time, params)
            new_values.append(new_time)
            last_time = new_time

        return new_values

    @load_case_name(parse_t_name, "case")
    @load_json_vals("original/", parse_t_name, "values", "parse_time")
    @load_json_vals("expected/", parse_t_name, "exp_vals", "parse_time", True)
    @load_parameters()
    # @unittest.skip("skip")
    def test_parse_time_case3(self, case, values, exp_vals, params):
        """Parse a list of time values using _parse_time method."""
        strategy = ParseComposedQuarterTime1
        new_values = self.parse_time_values(strategy, values, params)

        msg = " ".join([str(case), ":", str(new_values),
                        "are not equal to", str(exp_vals)])
        assert new_values == exp_vals, msg

    @load_case_name(parse_t_name, "case")
    @load_json_vals("original/", parse_t_name, "values", "parse_time")
    @load_json_vals("expected/", parse_t_name, "exp_vals", "parse_time", True)
    @load_parameters()
    # @unittest.skip("skip")
    def test_parse_time_case4(self, case, values, exp_vals, params):
        """Parse a list of time values using _parse_time method."""

        strategy = ParseComposedQuarterTime2
        new_values = self.parse_time_values(strategy, values, params)

        msg = " ".join([str(case), ":", str(new_values),
                        "are not equal to", str(exp_vals)])
        assert new_values == exp_vals, msg

    @load_case_name(parse_t_name, "case")
    @load_json_vals("original/", parse_t_name, "values", "parse_time")
    @load_json_vals("expected/", parse_t_name, "exp_vals", "parse_time", True)
    @load_parameters()
    # @unittest.skip("skip")
    def test_parse_time_case5(self, case, values, exp_vals, params):
        """Parse a list of time values using _parse_time method."""
        strategy = ParseComposedMonthTime1
        new_values = self.parse_time_values(strategy, values, params)

        msg = " ".join([str(case), ":", str(new_values),
                        "are not equal to", str(exp_vals)])
        assert new_values == exp_vals, msg

    @load_case_name(parse_t_name, "case")
    @load_json_vals("original/", parse_t_name, "values", "parse_time")
    @load_json_vals("expected/", parse_t_name, "exp_vals", "parse_time", True)
    @load_parameters()
    # @unittest.skip("skip")
    def test_parse_time_case5b(self, case, values, exp_vals, params):
        """Parse a list of time values using _parse_time method."""

        strategy = ParseComposedMonthTime2
        new_values = self.parse_time_values(strategy, values, params)

        msg = " ".join([str(case), ":", str(new_values),
                        "are not equal to", str(exp_vals)])
        assert new_values == exp_vals, msg

    # @load_case_name(parse_t_name, "case")
    # @load_json_vals("original/", parse_t_name, "values", "parse_time")
    # @load_json_vals("expected/", parse_t_name, "exp_vals", "parse_time", True)
    # @load_parameters()
    @unittest.skip("skip")
    def test_parse_time_case6(self, case, values, exp_vals, params):
        """Parse a list of time values using _parse_time method."""

        strategy = None  # TODO: Implement a strategy for this case!
        new_values = self.parse_time_values(strategy, values, params)

        msg = " ".join([str(case), ":", str(new_values),
                        "are not equal to", str(exp_vals)])
        assert new_values == exp_vals, msg

    # @load_case_name(parse_t_name, "case")
    # @load_json_vals("original/", parse_t_name, "values", "parse_time")
    # @load_json_vals("expected/", parse_t_name, "exp_vals", "parse_time", True)
    # @load_parameters()
    @unittest.skip("skip")
    def test_parse_time_case6b(self, case, values, exp_vals, params):
        """Parse a list of time values using _parse_time method."""

        strategy = None  # TODO: Implement a strategy for this case!
        new_values = self.parse_time_values(strategy, values, params)

        msg = " ".join([str(case), ":", str(new_values),
                        "are not equal to", str(exp_vals)])
        assert new_values == exp_vals, msg

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
    # unittest.main()
