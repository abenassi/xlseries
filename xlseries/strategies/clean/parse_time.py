#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
parse_time
----------------------------------

This module contains strategies to parse time strings of different frequencies.
"""

import sys
import inspect
from pprint import pprint
import datetime
import parsley


class BaseParseTimeStrategy(object):

    """BaseParseTimeStrategy class for all parse time strategies."""

    # PUBLIC INTERFACE
    @classmethod
    def accepts(cls, curr_time, last_time, params):
        return cls._accepts(curr_time, last_time, params)

    @classmethod
    def parse_time(cls, curr_time, last_time, params):
        return cls._parse_time(curr_time, last_time, params)

    @classmethod
    def _parse_time(cls, curr_time, last_time, params):

        # time format is correct
        if type(curr_time) == params["time_format"]:
            time_value = curr_time

        # fix strings time formats
        elif type(curr_time) == str or type(curr_time) == unicode:
            grammar = cls.make_parsley_grammar()
            result = grammar(curr_time).date()

            # take new date elements found with the grammar
            year = result[0] or last_time.year
            month = result[1] or last_time.month
            day = result[2] or last_time.day

            time_value = datetime.datetime(year, month, day)

        # no time could be parsed from the value
        else:
            time_value = None

        return time_value


class ParseSimpleTime(BaseParseTimeStrategy):

    """Parse dates in datetime or very easy time string to parse."""

    @classmethod
    def _accepts(cls, curr_time, last_time, params):
        return not params["time_multicolumn"] and not params["time_composed"]

    @classmethod
    def _parse_time(cls, curr_time, last_time, params):

        # time format is correct
        if type(curr_time) == params["time_format"]:
            time_value = curr_time

        # fix strings time formats
        elif type(curr_time) == str or type(curr_time) == unicode:
            str_value = curr_time.replace(".", "-").replace("/", "-")
            str_format = "%d-%m-%y"
            time_value = datetime.datetime.strptime(str_value, str_format)

        # no time could be parsed from the value
        else:
            time_value = None

        return time_value


class BaseComposedQuarter(BaseParseTimeStrategy):

    """Parse dates from strings composed by substrings with date info.
    Only for quarterly series."""

    @classmethod
    def _accepts(cls, curr_time, last_time, params):
        # print params
        return not params["time_multicolumn"] and params["time_composed"]

    @staticmethod
    def _quarter_num_to_month(quarter_number):

        if int(quarter_number) == 1:
            month = 1
        elif int(quarter_number) == 2:
            month = 4
        elif int(quarter_number) == 3:
            month = 7
        else:
            month = 10

        return month


class ParseComposedQuarterTime1(BaseComposedQuarter):

    """Parse quarterly dates from strings composed by substrings with date
    info."""

    @classmethod
    def _accepts(cls, curr_time, last_time, params):
        print params
        return not params["time_multicolumn"] and params["time_composed"] and \
            params["frequency"] == "Q"

    @classmethod
    def make_parsley_grammar(cls):
        return parsley.makeGrammar("""
                not_digit = anything:x ?(x not in "0123456789")

                year = not_digit* <digit{4}>:y ws -> int(y)
                q_number = not_digit* digit:q_num not_digit* -> int(q_num)

                date = year?:y q_number:q_num -> (y, q_to_m(q_num), 1)
                """, {"q_to_m": cls._quarter_num_to_month})


def get_strategies_names():
    """Returns a list of the parsers names, whith no Base classes."""

    list_cls_tuple = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    list_cls_names = [cls_tuple[0] for cls_tuple in list_cls_tuple]
    list_no_base_cls_names = [cls_name for cls_name in list_cls_names
                              if cls_name[:4] != "Base" and
                              cls_name != "Parameters"]

    return list_no_base_cls_names


def get_strategies():
    """Returns a list of references to the parsers classes."""

    return [globals()[cls_name] for cls_name in get_strategies_names()]


if __name__ == '__main__':
    pprint(sorted(get_strategies_names()))
