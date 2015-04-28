#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
clean_ti_strategies
----------------------------------

This module contains strategies to parse and clean time indexes in worksheets
cotaining time data series.

Warning! Do not import other classes directly "from module import Class",
except if they are custom exceptions.
Rather import the module in which the Class is defined and use it like
"module.Class". All the classes defined in this modul namespace are
automatically taken by "get_strategies" and exposed to the user.
"""

import arrow
from pprint import pprint
from openpyxl.cell import column_index_from_string

from xlseries.strategies.clean.parse_time import NoTimeValue
import xlseries.utils.strategies_helpers
from xlseries.utils.time_manipulation import increment_time
import xlseries.strategies.clean.parse_time as parse_time_strategies


# CUSTOM EXCEPTIONS
class TimeValueGoingBackwards(Exception):

    """Raised when a time value is going backwards.

    The parser observe that a time value is going backwards and
    existent strategies can't deal with it."""
    pass


class NoExpectedTimeValue(Exception):

    """Raised when no expected time value is provided to compare."""
    pass


class TimeValueGoingForth(Exception):

    """Raised when time value is going forth, when not supposed to.

    The parser observe that a time value is going forth than expected
    and existent strategies can't deal with it."""
    pass


class TimeParsingError(Exception):

    """Raised when parsing to date data structure is impossible.

    There is no strategy to deal with the time value that is trying to be
    parsed."""
    pass

# STRATEGIES


class BaseCleanTiStrategy(object):

    """BaseCleanTiStrategy class for all time index cleaning strategies."""

    MAX_IMPL = 20

    # PUBLIC INTERFACE
    @classmethod
    def accepts(cls, ws, params):
        return cls._accepts(ws, params)

    @classmethod
    def clean_time_index(cls, ws, params):
        return cls._clean_time_index(ws, params)

    # PRIVATE
    @classmethod
    def _correct_progression(cls, last_time_value, curr_time_value,
                             freq, missings, missing_value):

        exp_time_value = increment_time(last_time_value, 1, freq)
        assert type(exp_time_value) == arrow.Arrow
        assert type(last_time_value) == arrow.Arrow or not last_time_value
        assert type(curr_time_value) == arrow.Arrow
        # print last_time_value, curr_time_value, exp_time_value,
        # curr_time_value == exp_time_value, missing_value

        if not exp_time_value:
            msg = "No expected time value could be calcualted from " + \
                unicode(last_time_value) + " " + unicode(freq)
            raise NoExpectedTimeValue(msg)

        # everything is ok!
        if exp_time_value == curr_time_value:
            return curr_time_value

        # going back
        if curr_time_value < last_time_value:
            if cls._time_value_typo(curr_time_value, exp_time_value):
                return exp_time_value
            else:
                msg = "".join(["Current:", unicode(curr_time_value),
                               "Expected:", unicode(exp_time_value),
                               "Last:", unicode(last_time_value)])
                raise TimeValueGoingBackwards(msg)

        # going forth with no missings allowed
        going_forth = curr_time_value > last_time_value
        if going_forth and not missings:
            if cls._time_value_typo(curr_time_value, exp_time_value):
                return exp_time_value
            else:
                msg = "".join(["Current:", unicode(curr_time_value),
                               "Expected:", unicode(exp_time_value),
                               "Last:", unicode(last_time_value)])
                raise TimeValueGoingForth(msg)

        # going forth with implicit missings
        max_forth_time_value = increment_time(last_time_value,
                                              cls.MAX_IMPL, freq)
        going_too_forth = curr_time_value > max_forth_time_value
        if going_too_forth and missings and missing_value == "Implicit":
            forth_time_value = cls._forth_time_value_typo(curr_time_value,
                                                          max_forth_time_value)
            if forth_time_value:
                return forth_time_value
            else:
                return False

        # everything should be ok
        else:
            return curr_time_value

    @classmethod
    def _time_value_typo(cls, curr_time_value, exp_time_value):
        """Check if a time value could have a human typo.

        It relies in the idea that if the current time value being
        parsed is equal in two of the three parameters of a date
        (day, month and year), the different one is a human typo.

        Args:
            curr_time_value: Time value to be analyzed for a typo.
            exp_time_value: Expected time value to compare.
        """

        matches = [(curr_time_value.day == exp_time_value.day),
                   (curr_time_value.month == exp_time_value.month),
                   (curr_time_value.year == exp_time_value.year)]

        if matches.count(True) == 2:
            return True
        else:
            return False

    @classmethod
    def _forth_time_value_typo(cls, curr_time_value, max_forth_time_value):

        day_typo = arrow.get(year=curr_time_value.year,
                             month=curr_time_value.month,
                             day=max_forth_time_value.day)

        month_typo = arrow.get(year=curr_time_value.year,
                               month=max_forth_time_value.month,
                               day=curr_time_value.day)

        year_typo = arrow.get(year=max_forth_time_value.year,
                              month=curr_time_value.month,
                              day=curr_time_value.day)

        for possible_typo in [day_typo, month_typo, year_typo]:
            if possible_typo < max_forth_time_value:
                return possible_typo

        return None

    @classmethod
    def _parse_time(cls, curr_time, last_time, params):
        """Try to parse any value into a proper date format.

        Iterate a pool of strategies looking one that understands the format of
        the time value to be parsed and declares to be able to parse it into
        a date format.

        Args:
            curr_time: Value to be parsed into a date format.
            last_time: Last value parsed, as reference for some strategies.
            params: Parameters of the series being analyzed.

        Returns:
            An arrow.Arrow object expressing a date.
        """

        if curr_time:
            for strategy in parse_time_strategies.get_strategies():
                if strategy.accepts(curr_time, last_time, params):
                    # print strategy, "was accepted!"
                    time_value = strategy.parse_time(curr_time, last_time,
                                                     params)

                    msg = "".join([unicode(time_value), " - ",
                                   unicode(type(time_value)),
                                   " is not arrow.Arrow",
                                   "\nValue parsed: ", unicode(curr_time)])
                    assert type(time_value) == arrow.Arrow, msg

                    return time_value

        msg = "".join(["No strategy to parse\nCurrent: ", unicode(curr_time),
                       "\nLast: ", unicode(last_time),
                       "\nParameters: ", repr(params)])
        raise TimeParsingError(msg)


class CleanSingleColumnTi(BaseCleanTiStrategy):

    """Clean time indexes that use a single column."""

    # PRIVATE INTERFACE METHODS
    @classmethod
    def _accepts(cls, ws, params):
        return not params["time_multicolumn"]

    @classmethod
    def _clean_time_index(cls, ws, params):
        """Extract time data series and return them as data frames."""

        p = params

        # the col doesn't change in all the iteration
        col = column_index_from_string(ws[p["time_header_coord"]].column)

        # iterate series time index values and clean them
        last_time = None
        for row in xrange(p["data_starts"], p["data_ends"] + 1):
            # raise Exception(row, p["data_starts"], p["data_ends"] + 1)

            # take the current time value to clean
            curr_time = ws.cell(row=row, column=col).value

            # only clean if the value is not None
            if curr_time:

                # print curr_time
                try:
                    # convert strings and datetime.datetime's to arrow.Arrow times
                    curr_time = cls._parse_time(curr_time, last_time, params)

                    # correct date typos checking a healthy time progression
                    if last_time:
                        curr_time = cls._correct_progression(last_time,
                                                             curr_time,
                                                             p["frequency"],
                                                             p["missings"],
                                                             p["missing_value"])

                    if not curr_time:
                        raise NoTimeValue
                        
                    ws.cell(row=row, column=col).value = curr_time.datetime
                    last_time = curr_time

                except NoTimeValue:
                    pass



def get_strategies():
    return xlseries.utils.strategies_helpers.get_strategies()

if __name__ == '__main__':
    pprint(sorted(xlseries.utils.strategies_helpers.get_strategies_names()))
