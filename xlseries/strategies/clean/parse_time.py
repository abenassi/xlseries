#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
parse_time

This module contains strategies to parse time strings of different frequencies.
Up to this momment, all the strategies need to know the frequency of the time
string in advance (yearly, quarterly, monthly..)

The preconditions of all the strategies is that the strings passed to them must
be time values, otherwise an exception will be raised.
"""

from __future__ import unicode_literals
from pprint import pprint
import arrow
import datetime
import parsley

from xlseries.utils.time_manipulation import increment_time
import xlseries.utils.strategies_helpers


# EXCEPTIONS
class NoPossibleTimeValue(ValueError):

    """Raised if the value is not a possible time value."""

    def __init__(self, value):
        msg = " ".join([unicode(type(value)), unicode(value),
                        "is not a possible time value."])
        super(NoPossibleTimeValue, self).__init__(msg)


class NoTimeValue(ValueError):

    """Raised if the value is not an arrow.Arrow time value."""

    def __init__(self, value, last_time=None, next_time=None):
        msg = " ".join([unicode(type(value)), unicode(value),
                        "is not an arrow.Arrow time value."])
        if last_time:
            msg += "\nLast:" + unicode(last_time)
        if next_time:
            msg += "\nNext:" + unicode(next_time)

        super(NoTimeValue, self).__init__(msg)


class BaseDateMemberOutOfRange(ValueError):

    """Part of the result of a parsing grammar is out of range for a date."""

    def __init__(self, curr_time, grammar_result):
        msg = " ".join(["Time value doesn't make sense.",
                        unicode(curr_time), "has been converted into",
                        unicode(grammar_result)])
        super(BaseDateMemberOutOfRange, self).__init__(msg)


class DayOutOfRange(BaseDateMemberOutOfRange):

    """Raised if a day in a parsed time value is out of range."""


class MonthOutOfRange(BaseDateMemberOutOfRange):

    """Raised if a month in a parsed time value is out of range."""


# STRATEGIES
class BaseParseTimeStrategy(object):

    """BaseParseTimeStrategy class for all parse time strategies."""

    # PUBLIC INTERFACE
    @classmethod
    def accepts(cls, params, curr_time, last_time=None, next_time=None):
        """Check the inputs to see if the strategy can handle them.

        This base accepts() method check that the value is either already a
        time value or that could be a string expressing time before. In the
        latter it will call the private _accepts() method of the concrete
        strategy being called to see if it can be handled.

        Args:
            params: Parameters of the series being analyzed.
            curr_time: Value to be parsed into a date format.
            last_time: Last value parsed into time value.
            next_time: Next value to be parsed into time value.

        Returns:
            True or False meaning that a strategy declares it can handle the
                input.
        """

        if cls._already_time_value(curr_time):
            return True
        else:
            if not cls._possible_time_value(curr_time):
                raise NoPossibleTimeValue(curr_time)

            if not (type(last_time) == arrow.Arrow or last_time is None):
                raise NoTimeValue(last_time)

            return cls._accepts(params, curr_time, last_time, next_time)

    def parse_time(self, params, curr_time, last_time=None, next_time=None):
        """Parse a time string or value into a proper time value.

        Args:
            params: Parameters of the series being analyzed.
            curr_time: Value to be parsed into a date format.
            last_time: Last value parsed into time value.
            next_time: Next value to be parsed into time value.

        Returns:
            An arrow.Arrow time value.
        """
        # time format is correct
        if type(curr_time) == arrow.Arrow:
            return curr_time

        elif type(curr_time) == datetime.datetime:
            return arrow.get(curr_time)

        elif type(curr_time) == str or type(curr_time) == float:
            return self._parse_time(params, unicode(curr_time), last_time,
                                    next_time)
        else:
            assert type(curr_time) == unicode, "Current is not unicode."

            time_value = self._parse_time(params, curr_time,
                                          last_time, next_time)

            if not type(time_value) == arrow.Arrow:
                raise NoTimeValue(time_value, last_time, next_time)

            return time_value

    @classmethod
    def _parse_time(cls, params, curr_time, last_time=None, next_time=None):
        """Base _parse_time() method.

        Most of the concrete strategies subclassing BaseParseTimeStrategy will
        use this method and override only make_parsley_grammar() to change the
        grammar actually used to parse a time string. If the structure varies
        significantly or can be simpler, the entire _parse_time() method should
        be overriden.

        Args:
            curr_time: Time string to be parsed.
            last_time: Last time value (already parsed) in the time series
                being analyzed.
            params: A parameters dictionary with meta-data about the series
                being analyzed.

        Returns:
            An arrow.Arrow time value.
        """

        grammar = cls.make_parsley_grammar()
        result = grammar(curr_time).date()

        # take new date elements found with the grammar
        year = int(result[0] or last_time.year)
        month = int(result[1] or last_time.month)
        day = int(result[2] or last_time.day)

        # check date make sense
        if day not in range(1, 32):
            raise DayOutOfRange(curr_time, result)

        if month not in range(1, 13):
            raise MonthOutOfRange(curr_time, result)

        return arrow.get(year, month, day)

    @staticmethod
    def _dob_year_to_four(dob_year):
        """Convert a two digit year string in a four digits year string."""
        return arrow.Arrow.strptime(dob_year, "%y").year

    @classmethod
    def _already_time_value(cls, value):
        """Check if a value is already of a time value type."""
        return (type(value) == arrow.Arrow or type(value) == datetime.datetime)

    @classmethod
    def _possible_time_value(cls, value):
        """Check that a value could be a time value."""
        return (value is not None) and (type(value) != int)


class ParseSimpleTime(BaseParseTimeStrategy):

    """Parse dates expressed in a standard or very easy string to parse."""
    MAX_IMPL = 20

    def __init__(self, time_format=None):
        self.time_format = time_format

    @classmethod
    def _accepts(cls, params, curr_time, last_time=None, next_time=None):
        return not params["time_composed"]

    def _parse_time(self, params, curr_time, last_time=None, next_time=None):
        """Parse a string into a time value.

        Try different standard formats and check that the result make sense in
        the progression of the time series."""

        str_value = curr_time.replace(".", "-").replace("/", "-")
        time_value = None

        # first try with the last time format that worked
        if self.time_format:
            try:
                time_value = arrow.get(str_value, self.time_format)
                if not self._time_make_sense(params, time_value, last_time,
                                            next_time):
                    time_value = None

                if not type(time_value) == arrow.Arrow:
                    raise NoTimeValue(time_value, last_time, next_time)

                return time_value

            except:
                pass

        # if it doesn't work, try with everyone
        formats = list(self._get_possible_time_formats(str_value))
        for time_format in formats:
            # print curr_time, last_time, next_time, time_format, formats
            try:
                time_value = arrow.get(str_value, time_format)
            except Exception:
                continue

            if not self._time_make_sense(params, time_value, last_time,
                                        next_time):
                time_value = None
                continue

            else:
                break

        if not type(time_value) == arrow.Arrow:
            raise NoTimeValue(time_value, last_time, next_time)

        return time_value

    def _time_make_sense(self, params, time_value, last_time, next_time):
        """Check that a parsed time value make sense with the previous one.

        Args:
            params: Parameters of the time series.
            time_value: Recently parsed time value.
            last_time: Last time value that was parsed.
            next_time: Next value to be parsed into a time value.

        Returns:
            True or False, if the value make sense with the last one and the
                next one.
        """

        # making sense with the last value
        if last_time:
            is_after_last = time_value > last_time
            max_forth_time_value = increment_time(last_time, self.MAX_IMPL,
                                                  params["frequency"])
            is_not_too_after_last = time_value <= max_forth_time_value

        else:
            is_after_last, is_not_too_after_last = True, True

        # making sense with the next value
        if next_time:
            try:
                next_time = self.parse_time(params, next_time, time_value)
                is_before_next = time_value < next_time
                max_forth_time_value = increment_time(time_value,
                                                      self.MAX_IMPL,
                                                      params["frequency"])
                is_not_too_before_next = next_time <= max_forth_time_value

            except NoTimeValue:
                is_before_next, is_not_too_before_next = False, False

        else:
            is_before_next, is_not_too_before_next = True, True

        return (is_after_last and is_not_too_after_last and is_before_next and
                is_not_too_before_next)

    @staticmethod
    def _get_possible_time_formats(str_value):
        """Generate all possible time formats that could apply to str_value.

        Args:
            str_value: A string representing time.

        Yields:
            A possible time format for a given time string value.
        """
        # print str_value

        reps = map(len, str_value.split("-"))
        assert len(reps) == 3, "There is no 3 date elements in " + str_value

        for order in ["D-M-Y", "M-D-Y", "Y-M-D"]:
            time_format = "-".join([char * reps[i] for i, char in
                                    enumerate(order.split("-"))])
            # print
            yield time_format


class BaseComposedQuarter(BaseParseTimeStrategy):

    """Parse dates from strings composed by substrings with date info.
    Only for quarterly series."""

    @classmethod
    def _accepts(cls, params, curr_time, last_time=None, next_time=None):

        try:
            cls.make_parsley_grammar()(curr_time).date()
            match_grammar = True
        except:
            match_grammar = False

        return (params["time_composed"] and params["frequency"] == "Q" and
                match_grammar)

    @staticmethod
    def _quarter_num_to_month(quarter_number):
        """Convert a quarter number in the number of first month."""

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
    ...     new = ParseComposedQuarterTime1.parse_time(params, str_date, last)
    ...     last = new
    ...     print new
    1986-01-01T00:00:00+00:00
    1986-04-01T00:00:00+00:00
    1986-07-01T00:00:00+00:00
    1986-10-01T00:00:00+00:00
    """

    @classmethod
    def make_parsley_grammar(cls):
        """Return a parsley parsing expression grammar."""
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
    ...         "u' 3 Trim 07 2'",
    ...         "4° Trim 07 ",
    ...         "1° Trim 08 "]
    >>> params = {"time_format": str}
    >>>
    >>> last = None
    >>> for str_date in orig:
    ...     new = ParseComposedQuarterTime2.parse_time(params, str_date, last)
    ...     last = new
    ...     print new
    2007-04-01T00:00:00+00:00
    2007-07-01T00:00:00+00:00
    2007-10-01T00:00:00+00:00
    2008-01-01T00:00:00+00:00
    """

    @classmethod
    def make_parsley_grammar(cls):
        """Return a parsley parsing expression grammar."""
        return parsley.makeGrammar("""
                not_digit = anything:x ?(x not in "0123456789 ")

                q = not_digit* ws digit:q not_digit* ws -> int(q)
                y = (ws | not_digit) <digit{2}>:y (ws | not_digit) -> y

                date = q:q not_digit* y:y anything* -> (dob_year(y), q_to_m(q), 1)
                """, {"q_to_m": cls._quarter_num_to_month,
                      "dob_year": cls._dob_year_to_four})


class BaseComposedMonth(BaseParseTimeStrategy):

    """Parse dates from strings composed by substrings with date info.
    Only for quarterly series."""

    @classmethod
    def _accepts(cls, params, curr_time, last_time=None, next_time=None):

        # try to match grammar
        try:
            cls.make_parsley_grammar()(unicode(curr_time)).date()
            match_grammar = True
        except:
            match_grammar = False
        # raise Exception("Match grammar" + str(match_grammar))
        return (params["time_composed"] and
                params["frequency"] == "M" and match_grammar)

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
    ...     new = ParseComposedMonthTime1.parse_time(params, str_date, last)
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
        """Return a parsley parsing expression grammar."""
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
    ...     new = ParseComposedMonthTime2.parse_time(params, str_date, last)
    ...     last = new
    ...     print new
    1991-01-01T00:00:00+00:00
    1991-02-01T00:00:00+00:00
    1991-03-01T00:00:00+00:00
    1991-04-01T00:00:00+00:00
    """

    @classmethod
    def make_parsley_grammar(cls):
        """Return a parsley parsing expression grammar."""
        return parsley.makeGrammar("""
                not_digit = anything:x ?(x not in "0123456789 ")

                y = (ws | not_digit) <digit{4}>:y (ws | not_digit) -> int(y)
                m = (ws | not_digit) <digit{1, 2}>:m (ws | not_digit) -> int(m)

                y_m = y:y not_digit* m:m anything* -> (y, m, 1)
                m_y = m:m not_digit* y:y anything* -> (y, m, 1)

                date = y_m | m_y
                """, {})


def get_strategies():
    """Return all the concrete strategies available in this module.

    This method avoid to return base classes and exceptions."""

    return xlseries.utils.strategies_helpers.get_strategies()

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    pprint(sorted(xlseries.utils.strategies_helpers.get_strategies_names()))
