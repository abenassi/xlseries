#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_parse_time

Tests for `parse_time` module.
"""
import unittest
import nose
import arrow
import json
import os
from functools import wraps
import re
from mock import patch
import parsley

from xlseries.strategies.clean.parse_time import ParseComposedYear1
from xlseries.strategies.clean.parse_time import ParseComposedYear2
from xlseries.strategies.clean.parse_time import ParseComposedYearQuarter1
from xlseries.strategies.clean.parse_time import ParseComposedQuarterYear1
from xlseries.strategies.clean.parse_time import ParseComposedQuarter1
from xlseries.strategies.clean.parse_time import ParseComposedQuarter2
from xlseries.strategies.clean.parse_time import ParseComposedQuarter3
from xlseries.strategies.clean.parse_time import ParseComposedSemester
from xlseries.strategies.clean.parse_time import ParseComposedMonth1
from xlseries.strategies.clean.parse_time import ParseComposedMonth2
from xlseries.strategies.clean.parse_time import ParseSimpleTime
from xlseries.strategies.clean.parse_time import NoTimeValue
from xlseries.utils.case_loaders import load_parameters_case
from xlseries.utils.path_finders import abs_path


def load_case_number():
    """Decorate a test loading the case number taken from test name."""

    def fn_decorator(fn):
        last_word = fn.__name__.split("_")[-1]
        case_num = last_word.replace("case", "").strip()

        @wraps(fn)
        def fn_decorated(*args, **kwargs):
            kwargs["case_num"] = case_num
            fn(*args, **kwargs)

        return fn_decorated
    return fn_decorator


# @unittest.skip("skip")
class ParseSimpleTimeTest(unittest.TestCase):

    def run_pt(self, params, exp_value, value, last_time=None,
               next_value=None):
        new_value = ParseSimpleTime()._parse_time(params, value, last_time,
                                                  next_value)

        msg = " ".join([repr(new_value), "!=", repr(exp_value), "\n",
                        "value:", repr(value),
                        "last time:", repr(last_time),
                        "next value:", repr(next_value)])

        self.assertEqual(new_value, exp_value, msg)

    # @unittest.skip("skip")
    def test_parse_time_case2_normal_behaviour(self):
        params = load_parameters_case(2)

        last_time = arrow.get(2009, 12, 16)
        exp_value = arrow.get(2009, 12, 17)
        next_value = "18-12-09"

        self.run_pt(params[0], exp_value, "17-12.09", last_time, next_value)
        self.run_pt(params[0], exp_value, "12-17.09", last_time, next_value)
        self.run_pt(params[0], exp_value, "17-12.2009", last_time, next_value)
        self.run_pt(params[0], exp_value, "12-17.2009", last_time, next_value)
        self.run_pt(params[0], exp_value, "2009.12.17", last_time, next_value)

        self.run_pt(params[0], exp_value, "17-12.09", None, next_value)
        self.run_pt(params[0], exp_value, "12-17.09", None, next_value)
        self.run_pt(params[0], exp_value, "17-12.2009", None, next_value)
        self.run_pt(params[0], exp_value, "12-17.2009", None, next_value)
        self.run_pt(params[0], exp_value, "2009.12.17", None, next_value)

        self.run_pt(params[0], exp_value, "17-12.09", last_time, None)
        self.run_pt(params[0], exp_value, "12-17.09", last_time, None)
        self.run_pt(params[0], exp_value, "17-12.2009", last_time, None)
        self.run_pt(params[0], exp_value, "12-17.2009", last_time, None)
        self.run_pt(params[0], exp_value, "2009.12.17", last_time, None)

        exp_value = arrow.get(2010, 3, 2)
        last_time = arrow.get(2010, 3, 1)
        next_value = arrow.get(2010, 3, 3)
        self.run_pt(params[0], exp_value, "02.03.10", last_time, next_value)

    def test_parse_time_case2_exceptions(self):
        params = load_parameters_case(2)

        last_time = arrow.get(2009, 12, 16)
        next_value = "18-12-09"

        with patch.object(ParseSimpleTime, "_get_possible_time_formats",
                          return_value=["YY-MM-DD"]):
            value = "12-17.09"
            self.assertRaises(NoTimeValue, ParseSimpleTime()._parse_time,
                              params[0], value, last_time, next_value)

        with patch.object(ParseSimpleTime, "_get_possible_time_formats",
                          return_value=["MM-DD-YY"]):
            value = "17-12.09"
            self.assertRaises(NoTimeValue, ParseSimpleTime()._parse_time,
                              params[0], value, last_time, next_value)

    def test_parse_time_case4_invalid_date(self):
        no_time = u"Var. 4° Trim.13 / 4° Trim.12"
        last = arrow.get(2013, 10, 1).datetime

        with self.assertRaises(parsley.ParseError):
            ParseComposedQuarter2().parse_time({}, no_time, last)

    def test_time_make_sense(self):

        params = load_parameters_case(2)
        time_value = arrow.get(2017, 12, 9)
        last_time = arrow.get(2009, 12, 16)
        next_value = "18-12-09"

        make_sense = ParseSimpleTime()._time_make_sense(params[0],
                                                        time_value, last_time,
                                                        next_value)
        self.assertFalse(make_sense)

        make_sense = ParseSimpleTime()._time_make_sense(params[0],
                                                        time_value, None,
                                                        next_value)
        self.assertFalse(make_sense)

        time_value = arrow.get(2002, 3, 10)
        last_time = arrow.get(2010, 3, 1)

        make_sense = ParseSimpleTime()._time_make_sense(params[0],
                                                        time_value, last_time,
                                                        next_value)
        self.assertFalse(make_sense)

        time_value = arrow.get(2010, 2, 3)
        last_time = arrow.get(2010, 3, 1)
        next_value = arrow.get(2010, 3, 3)

        make_sense = ParseSimpleTime()._time_make_sense(params[0],
                                                        time_value, last_time,
                                                        next_value)
        self.assertFalse(make_sense)

        time_value = arrow.get(2010, 3, 2)
        last_time = arrow.get(2010, 3, 1)
        next_value = arrow.get(2010, 3, 3)

        make_sense = ParseSimpleTime()._time_make_sense(params[0],
                                                        time_value, last_time,
                                                        next_value)
        self.assertTrue(make_sense)

    def test_get_possible_time_formats(self):
        gen = ParseSimpleTime()._get_possible_time_formats("02-03-10")
        self.assertEqual(set(gen), set(["DD-MM-YY", "MM-DD-YY", "YY-MM-DD"]))

        gen = ParseSimpleTime()._get_possible_time_formats("02-03-2010")
        self.assertEqual(set(gen), set(["DD-MM-YYYY", "MM-DD-YYYY",
                                        "YY-MM-DDDD"]))


class ParseComposedTimeTest(unittest.TestCase):

    def parse_time_values(self, strategy, values, params):

        last_time = None

        new_values = []
        for value in values:
            # print value.encode("utf-8", "ignore")
            new_time = strategy().parse_time(params, value, last_time)
            new_values.append(new_time)
            last_time = new_time

        return new_values

    def run_parse_time_case(self, case_num, strategy, external=False):
        """Run a parse time test case using provided strategy.

        Args:
            case_num: Number of case to load.
            strategy: Strategy to parse the case.
        """
        if not external:
            case = "test_case" + str(case_num)
        else:
            case = "external_case" + str(case_num)

        with open(os.path.join(abs_path("original"),
                               "parse_time.json")) as f:
            values = json.load(f)[case]

        with open(os.path.join(abs_path("expected"),
                               "parse_time.json")) as f:
            exp_vals = json.load(f)[case]
            exp_vals = [eval(value) for value in exp_vals]

        rule = re.compile("(\d)")
        case_num_int = int(rule.match(case_num).group())
        if external:
            params = load_parameters_case(1)
        else:
            params = load_parameters_case(case_num_int)

        new_values = self.parse_time_values(strategy, values, params)

        msg = " ".join([str(case), ":", str(new_values),
                        "are not equal to", str(exp_vals)])
        self.assertEqual(new_values, exp_vals, msg)

    @load_case_number()
    # @unittest.skip("skip")
    def test_parse_time_case3(self, case_num):
        """Parse a list of time values using _parse_time method."""
        self.run_parse_time_case(case_num, ParseComposedQuarter1)

    @load_case_number()
    # @unittest.skip("skip")
    def test_parse_time_case4(self, case_num):
        """Parse a list of time values using _parse_time method."""
        self.run_parse_time_case(case_num, ParseComposedQuarter2)

    @load_case_number()
    # @unittest.skip("skip")
    def test_parse_time_case5(self, case_num):
        """Parse a list of time values using _parse_time method."""
        self.run_parse_time_case(case_num, ParseComposedMonth1)

    @load_case_number()
    # @unittest.skip("skip")
    def test_parse_time_case5b(self, case_num):
        """Parse a list of time values using _parse_time method."""
        self.run_parse_time_case(case_num, ParseComposedMonth2)

    @load_case_number()
    # @unittest.skip("skip")
    def test_parse_time_case6(self, case_num):
        """Parse a list of time values from case6 using _parse_time method."""
        self.run_parse_time_case(case_num, ParseComposedYearQuarter1)

    @load_case_number()
    # @unittest.skip("skip")
    def test_parse_time_case6b(self, case_num):
        """Parse a list of time values from case6b using _parse_time method."""
        self.run_parse_time_case(case_num, ParseComposedYearQuarter1)

    @load_case_number()
    # @unittest.skip("skip")
    def test_parse_time_case7(self, case_num):
        """Parse a list of time values from case7 using _parse_time method."""
        self.run_parse_time_case(case_num, ParseComposedYear1)

    @load_case_number()
    # @unittest.skip("skip")
    def test_parse_time_external_case1(self, case_num):
        """Parse a list of time values from external case 1."""
        self.run_parse_time_case(case_num, ParseComposedMonth1, True)

    @load_case_number()
    # @unittest.skip("skip")
    def test_parse_time_external_case2(self, case_num):
        """Parse a list of time values from external case 2."""
        self.run_parse_time_case(case_num, ParseComposedMonth1, True)

    @load_case_number()
    # @unittest.skip("skip")
    def test_parse_time_external_case3(self, case_num):
        """Parse a list of time values from external case 3."""
        self.run_parse_time_case(case_num, ParseComposedQuarter1, True)

    @load_case_number()
    # @unittest.skip("skip")
    def test_parse_time_external_case4(self, case_num):
        """Parse a list of time values from external case 4."""
        self.run_parse_time_case(case_num, ParseComposedMonth1, True)

    @load_case_number()
    # @unittest.skip("skip")
    def test_parse_time_external_case5(self, case_num):
        """Parse a list of time values from external case 5."""
        self.run_parse_time_case(case_num, ParseComposedQuarterYear1, True)

    @load_case_number()
    # @unittest.skip("skip")
    def test_parse_time_external_case6(self, case_num):
        """Parse a list of time values from external case 6."""
        self.run_parse_time_case(case_num, ParseComposedQuarter3, True)

    @load_case_number()
    # @unittest.skip("skip")
    def test_parse_time_external_case7(self, case_num):
        """Parse a list of time values from external case 7."""
        self.run_parse_time_case(case_num, ParseComposedQuarter3, True)

    @load_case_number()
    # @unittest.skip("skip")
    def test_parse_time_external_case8(self, case_num):
        """Parse a list of time values from external case 8."""
        self.run_parse_time_case(case_num, ParseComposedQuarter3, True)

    @load_case_number()
    # @unittest.skip("skip")
    def test_parse_time_external_case9(self, case_num):
        """Parse a list of time values from external case 9."""
        self.run_parse_time_case(case_num, ParseComposedQuarter3, True)

    @load_case_number()
    # @unittest.skip("skip")
    def test_parse_time_external_case10(self, case_num):
        """Parse a list of time values from external case 9."""
        self.run_parse_time_case(case_num, ParseComposedYear2, True)

    @load_case_number()
    # @unittest.skip("skip")
    def test_parse_time_external_case11(self, case_num):
        """Parse a list of time values from external case 9."""
        self.run_parse_time_case(case_num, ParseComposedSemester, True)


if __name__ == '__main__':
    nose.run(defaultTest=__name__)
    # unittest.main()
