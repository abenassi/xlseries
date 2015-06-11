#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
clean_ti_strategies

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
from pprint import pformat

from xlseries.strategies.clean.parse_time import NoTimeValue
from xlseries.strategies.clean.parse_time import DayOutOfRange, MonthOutOfRange
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
                msg = " ".join(["Current:", unicode(curr_time_value),
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
        """Check for a typo in day, month or year.

        This check is based on the idea that one of the three elements of
        the date is wrong because of a typo that makes the date greater than a
        possible maximum. When one of the possibilities generates a date lower
        than maximum it means the typo was succesfully corrected.

        Args:
            curr_time_value (arrow.Arrow): Time value being analyzed because
                it is greater than it should be.
            max_forth_time_value (arrow.Arrow): Maximum possible time value for
                curr_time_value being analyzed.

        Returns:
            arrow.Arrow or None: A fixed time value removing the typo or None
                if the typo couldn't be fixed.
        """

        day_typo = arrow.get(curr_time_value.year,
                             curr_time_value.month,
                             max_forth_time_value.day)

        month_typo = arrow.get(curr_time_value.year,
                               max_forth_time_value.month,
                               curr_time_value.day)

        year_typo = arrow.get(max_forth_time_value.year,
                              curr_time_value.month,
                              curr_time_value.day)

        for possible_typo in [day_typo, month_typo, year_typo]:
            if possible_typo < max_forth_time_value:
                return possible_typo

        return None

    @classmethod
    def _parse_time(cls, params, curr_time, last_time=None, next_value=None):
        """Try to parse any value into a proper date format.

        Iterate a pool of strategies looking one that understands the format of
        the time value to be parsed and declares to be able to parse it into
        a date format.

        Args:
            params: Parameters of the series being analyzed.
            curr_time: Value to be parsed into a date format.
            last_time: Last value parsed into time value.
            next_value: Next value to be parsed into time value.

        Returns:
            An arrow.Arrow object expressing a date.
        """

        if curr_time:
            for strategy in parse_time_strategies.get_strategies():
                if strategy.accepts(params, curr_time, last_time, next_value):
                    try:
                        time_value = strategy.parse_time(params, curr_time,
                                                         last_time,
                                                         next_value)

                    except (DayOutOfRange, MonthOutOfRange):
                        return None

                    msg = "".join([unicode(time_value), " - ",
                                   unicode(type(time_value)),
                                   " is not arrow.Arrow",
                                   "\nValue parsed: ", unicode(curr_time)])
                    assert type(time_value) == arrow.Arrow, msg

                    return time_value

        else:
            return None

        msg = "".join(["No strategy to parse\nCurrent: ", unicode(curr_time),
                       "\nLast: ", unicode(last_time),
                       "\nParameters: ", pformat(params)])
        raise TimeParsingError(msg)


class CleanSingleColumnTi(BaseCleanTiStrategy):

    """Clean time indexes that use a single column different to data column."""

    # PRIVATE INTERFACE METHODS
    @classmethod
    def _accepts(cls, ws, params):
        return not params["time_multicolumn"] and params["time_alignment"] == 0

    @classmethod
    def _clean_time_index(cls, ws, params):
        """Parse time strings into time values, cleaning the time index.

        Replace the value in the cell with the clean time value."""

        p = params
        col = cls._get_time_write_col(ws, p["time_header_coord"])

        # iterate series time index values and clean them
        last_time = None
        for row in xrange(p["data_starts"], p["data_ends"] + 1):

            # take the current time value to clean
            curr_time = cls._get_time_value(ws, row, p["time_header_coord"])
            next_time = cls._get_time_value(ws, row + 1,
                                            p["time_header_coord"])

            # only clean if the value is not None
            if cls._possible_time_value(curr_time):
                # convert strings and datetime.datetime's to arrow.Arrow
                # times
                # print curr_time, last_time, next_time
                curr_time = cls._parse_time(params, curr_time, last_time,
                                            next_time)

                if curr_time:
                    # correct date typos checking a healthy time progression
                    if last_time and curr_time:
                        curr_time = cls._correct_progression(last_time,
                                                             curr_time,
                                                             p["frequency"],
                                                             p["missings"],
                                                             p["missing_value"])

                    if curr_time and type(curr_time) != arrow.Arrow:
                        raise NoTimeValue

                    ws.cell(row=row, column=col).value = curr_time.datetime
                    last_time = curr_time

                else:
                    ws.cell(row=row, column=col).value = None

    @classmethod
    def _possible_time_value(cls, value):
        return value is not None and len(unicode(value).strip()) > 0

    @classmethod
    def _get_time_write_col(cls, ws, time_header_coord):
        """Returns the column where clean time index shouls be written."""
        return column_index_from_string(ws[time_header_coord].column)

    @classmethod
    def _get_time_value(cls, ws, row, time_header_coord):
        """Returns the time value corresponding a certain series and row."""
        col = cls._get_time_write_col(ws, time_header_coord)
        return ws.cell(row=row, column=col).value


class CleanSingleColumnTiOffsetTi(CleanSingleColumnTi):

    """Clean time indexes that use a single column with offset time alignment
    sharing the same column with the data.

    In this case, floats must not try to parsed because they will be data."""

    @classmethod
    def _accepts(cls, ws, params):
        return not params["time_multicolumn"] and params["time_alignment"] != 0

    @classmethod
    def _possible_time_value(cls, value):
        return (value is not None and len(unicode(value).strip()) > 0 and
                type(value) != float)


class CleanMultipleColumnsTiConcat(CleanSingleColumnTi):

    """Clean time indexes that use multiple columns concatenating columns.

    Multiple columns will be just concatanated as strings and
    CleanSingleColumnTi will be used."""

    # PRIVATE INTERFACE METHODS
    @classmethod
    def _accepts(cls, ws, params):
        return params["time_multicolumn"]

    @classmethod
    def _get_time_write_col(cls, ws, time_header_coord):
        """Returns the column where clean time index shouls be written."""
        return column_index_from_string(ws[time_header_coord[0]].column)

    @classmethod
    def _get_time_value(cls, ws, row, time_header_coord):
        """Returns the time value corresponding a certain series and row.

        Concatenate all the values of the time header columns in a unique
        string."""

        time_value_list = []

        for coord in time_header_coord:
            col = column_index_from_string(ws[coord].column)
            value = unicode(ws.cell(row=row, column=col).value).strip()
            if not value:
                return None
            time_value_list.append(value)

        return " ".join(time_value_list)


def get_strategies():
    return xlseries.utils.strategies_helpers.get_strategies()

if __name__ == '__main__':
    pprint(sorted(xlseries.utils.strategies_helpers.get_strategies_names()))
