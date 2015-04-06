#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
parse_time
----------------------------------

This module contains strategies to parse time strings of different frequencies.
"""

from __future__ import unicode_literals
import sys
import inspect
from pprint import pprint
import arrow
import datetime
import parsley


class BaseParseTimeStrategy(object):

    """BaseParseTimeStrategy class for all parse time strategies."""

    # PUBLIC INTERFACE
    @classmethod
    def accepts(cls, curr_time, last_time, params):
        if type(curr_time) == arrow.Arrow or type(curr_time) == datetime.datetime:
            return True
        else:
            return cls._accepts(curr_time, last_time, params)

    @classmethod
    def parse_time(cls, curr_time, last_time, params):
        return cls._parse_time(curr_time, last_time, params)

    @classmethod
    def _parse_time(cls, curr_time, last_time, params):

        # time format is correct
        if type(curr_time) == arrow.Arrow:
            time_value = curr_time

        elif type(curr_time) == datetime.datetime:
            time_value = arrow.get(curr_time)

        elif type(curr_time) == str:
            return cls._parse_time(unicode(curr_time),
                                   last_time, params)

        # fix strings time formats
        elif type(curr_time) == unicode:
            # print curr_time
            grammar = cls.make_parsley_grammar()
            result = grammar(curr_time).date()

            # take new date elements found with the grammar
            year = result[0] or last_time.year
            month = result[1] or last_time.month
            day = result[2] or last_time.day

            time_value = arrow.get(year, month, day)

        # no time could be parsed from the value
        else:
            time_value = None

        return time_value

    @staticmethod
    def _dob_year_to_four(dob_year):
        return arrow.Arrow.strptime(dob_year, "%y").year


class ParseSimpleTime(BaseParseTimeStrategy):

    """Parse dates in datetime or very easy time string to parse."""

    @classmethod
    def _accepts(cls, curr_time, last_time, params):
        return not params["time_multicolumn"] and not params["time_composed"]

    @classmethod
    def _parse_time(cls, curr_time, last_time, params):
        # time format is correct
        if type(curr_time) == arrow.Arrow:
            time_value = curr_time

        elif type(curr_time) == datetime.datetime:
            time_value = arrow.get(curr_time)

        # fix strings time formats
        elif type(curr_time) == str or type(curr_time) == unicode:
            str_value = curr_time.replace(".", "-").replace("/", "-")
            str_format = "DD-MM-YY"
            # print "here", str_value, str_format
            time_value = arrow.get(str_value, str_format)

        # no time could be parsed from the value
        else:
            time_value = None

        return time_value


class BaseComposedQuarter(BaseParseTimeStrategy):

    """Parse dates from strings composed by substrings with date info.
    Only for quarterly series."""

    @classmethod
    def _accepts(cls, curr_time, last_time, params):

        try:
            cls.make_parsley_grammar()(curr_time).date()
            match_grammar = True
        except:
            match_grammar = False

        return not params["time_multicolumn"] and params["time_composed"] and \
            params["frequency"] == "Q" and match_grammar

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
    info of the structure showed in the example.

    >>> orig = ["'1986    1º trim.",
    ...     "'            2º trim.",
    ...     "'            3º trim.",
    ...     "'            4º trim."]
    >>> params = {"time_format": str}
    >>>
    >>> last = None
    >>> for str_date in orig:
    ...     new = ParseComposedQuarterTime1.parse_time(str_date, last, params)
    ...     last = new
    ...     print new
    1986-01-01T00:00:00+00:00
    1986-04-01T00:00:00+00:00
    1986-07-01T00:00:00+00:00
    1986-10-01T00:00:00+00:00
    """

    @classmethod
    def make_parsley_grammar(cls):
        return parsley.makeGrammar("""
                not_digit = anything:x ?(x not in "0123456789")

                year = not_digit* <digit{4}>:y ws -> int(y)
                q_number = not_digit* digit:q_num not_digit* -> int(q_num)

                date = year?:y q_number:q_num -> (y, q_to_m(q_num), 1)
                """, {"q_to_m": cls._quarter_num_to_month})


class ParseComposedQuarterTime2(BaseComposedQuarter):

    """Parse quarterly dates from strings composed by substrings with date
    info of the structure showed in the example.

    >>> orig = [u"2° Trim 07",
    ...         "3° Trim 07 2",
    ...         "4° Trim 07 ",
    ...         "1° Trim 08 "]
    >>> params = {"time_format": str}
    >>>
    >>> last = None
    >>> for str_date in orig:
    ...     new = ParseComposedQuarterTime2.parse_time(str_date, last, params)
    ...     last = new
    ...     print new
    2007-04-01T00:00:00+00:00
    2007-07-01T00:00:00+00:00
    2007-10-01T00:00:00+00:00
    2008-01-01T00:00:00+00:00
    """

    @classmethod
    def make_parsley_grammar(cls):
        return parsley.makeGrammar("""
                not_digit = anything:x ?(x not in "0123456789 ")

                q = not_digit* digit:q not_digit* ws -> int(q)
                y = (ws | not_digit) <digit{2}>:y (ws | not_digit) -> y

                date = q:q not_digit* y:y anything* -> (dob_year(y), q_to_m(q), 1)
                """, {"q_to_m": cls._quarter_num_to_month,
                      "dob_year": cls._dob_year_to_four})


class BaseComposedMonth(BaseParseTimeStrategy):

    """Parse dates from strings composed by substrings with date info.
    Only for quarterly series."""

    @classmethod
    def _accepts(cls, curr_time, last_time, params):

        # try to match grammar
        try:
            cls.make_parsley_grammar()(curr_time).date()
            match_grammar = True
        except:
            match_grammar = False

        return not params["time_multicolumn"] and params["time_composed"] and \
            params["frequency"] == "M" and match_grammar

    @classmethod
    def _month_str_to_num(cls, month_str):
        """Convert month string in month number.

        >>> BaseComposedMonth._month_str_to_num("ene")
        1
        >>> BaseComposedMonth._month_str_to_num("jan")
        1
        >>> BaseComposedMonth._month_str_to_num("september")
        9
        >>> BaseComposedMonth._month_str_to_num("septiembre")
        9
        """

        loc_iter = (arrow.locales.__dict__[l] for l in vars(arrow.locales)
                    if l[-6:] == "Locale")
        for local in loc_iter:
            month_num = local().month_number(month_str.capitalize())
            if month_num:
                break

        return month_num


class ParseComposedMonthTime1(BaseComposedMonth):

    """Parse quarterly dates from strings composed by substrings with date
    info of the structure showed in the example.

    >>> orig = ["1991    Ene. ",
    ...         "1991    Feb.",
    ...         "1991    Mar.",
    ...         "Abr.    1991",
    ...         "May.    1991"]
    >>> params = {"time_format": str}
    >>>
    >>> last = None
    >>> for str_date in orig:
    ...     new = ParseComposedMonthTime1.parse_time(str_date, last, params)
    ...     last = new
    ...     print new
    1991-01-01T00:00:00+00:00
    1991-02-01T00:00:00+00:00
    1991-03-01T00:00:00+00:00
    1991-04-01T00:00:00+00:00
    1991-05-01T00:00:00+00:00
    """

    @classmethod
    def make_parsley_grammar(cls):
        return parsley.makeGrammar("""
                not_digit = anything:x ?(x not in "0123456789 ")

                y = (ws | not_digit) <digit{4}>:y (ws | not_digit) -> int(y)
                m = ws <letter{3}>:m '.'? -> m

                y_m = y:y m:m anything* -> (y, month(m), 1)
                m_y = m:m y:y anything* -> (y, month(m), 1)

                date = y_m | m_y
                """, {"month": cls._month_str_to_num})


class ParseComposedMonthTime2(BaseComposedMonth):

    """Parse quarterly dates from strings composed by substrings with date
    info of the structure showed in the example.

    >>> orig = ["1991,01 ",
    ...         "1991,02  ",
    ...         " 03,1991  ",
    ...         "04,1991  "]
    >>> params = {"time_format": str}
    >>>
    >>> last = None
    >>> for str_date in orig:
    ...     new = ParseComposedMonthTime2.parse_time(str_date, last, params)
    ...     last = new
    ...     print new
    1991-01-01T00:00:00+00:00
    1991-02-01T00:00:00+00:00
    1991-03-01T00:00:00+00:00
    1991-04-01T00:00:00+00:00
    """

    @classmethod
    def make_parsley_grammar(cls):
        return parsley.makeGrammar("""
                not_digit = anything:x ?(x not in "0123456789 ")

                y = (ws | not_digit) <digit{4}>:y (ws | not_digit) -> int(y)
                m = (ws | not_digit) <digit{2}>:m (ws | not_digit) -> int(m)

                y_m = y:y not_digit* m:m anything* -> (y, m, 1)
                m_y = m:m not_digit* y:y anything* -> (y, m, 1)

                date = y_m | m_y
                """, {})


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
    import doctest
    doctest.testmod()
    pprint(sorted(get_strategies_names()))
