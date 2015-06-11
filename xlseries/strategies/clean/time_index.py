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

from xlseries.strategies.clean.parse_time import DayOutOfRange, MonthOutOfRange
import xlseries.utils.strategies_helpers
from xlseries.utils.time_manipulation import increment_time
import xlseries.strategies.clean.parse_time as parse_time_strategies


# CUSTOM EXCEPTIONS
class BaseProgressionError(ValueError):

    """Raised when the progression of a time value is wrong."""

    def get_msg(self, curr_time, exp_time, last_time):
        return " ".join(["Last:", unicode(last_time),
                         "\nExpected:", unicode(exp_time),
                         "\nCurrent:", unicode(curr_time)])


class TimeValueGoingBackwards(BaseProgressionError):

    """Raised when a time value is going backwards.

    The parser observe that a time value is going backwards and
    existent strategies can't deal with it."""

    def __init__(self, curr_time, exp_time, last_time):
        msg = self.get_msg(curr_time, exp_time, last_time)
        super(TimeValueGoingBackwards, self).__init__(msg)


class TimeValueGoingForth(BaseProgressionError):

    """Raised when time value is going forth, when not supposed to.

    The parser observe that a time value is going forth than expected
    and existent strategies can't deal with it."""

    def __init__(self, curr_time, exp_time, last_time):
        msg = self.get_msg(curr_time, exp_time, last_time)
        super(TimeValueGoingForth, self).__init__(msg)


class ParseTimeImplementationError(NotImplementedError):

    """Raised when parsing to date data structure is impossible.

    There is no strategy to deal with the time value that is trying to be
    parsed."""

    def __init__(self, curr_time, last_time, next_time, params):
        msg = " ".join(["No strategy to parse time.",
                        "\nCurrent:", unicode(curr_time),
                        "\nLast:", unicode(last_time),
                        "\nNext:", unicode(next_time),
                        "\nParameters: ", pformat(params)])
        super(ParseTimeImplementationError, self).__init__(msg)


# STRATEGIES
class BaseCleanTiStrategy(object):

    """BaseCleanTiStrategy class for all time index cleaning strategies."""

    # PUBLIC INTERFACE
    @classmethod
    def accepts(cls, ws, params):
        return cls._accepts(ws, params)

    @classmethod
    def clean_time_index(cls, ws, params):
        return cls._clean_time_index(ws, params)

    # PRIVATE main methods
    @classmethod
    def _accepts(cls, ws, params):
        raise NotImplementedError("Base cleaning time index strategy " +
                                  "doesn't accept inputs.")

    @classmethod
    def _clean_time_index(cls, ws, params):
        """Parse time strings into time values, cleaning the time index.

        If a value in a cell should be a time value, replace it with the clean
        time value."""

        p = params
        col = cls._get_time_write_col(ws, p["time_header_coord"])

        # iterate series time index values cleaning them
        last_time = None
        for row in xrange(p["data_starts"], p["data_ends"] + 1):

            # take take a possible time value that should be cleaned
            curr_time = cls._get_time_value(ws, row, p["time_header_coord"])
            next_time = cls._get_time_value(ws, row + 1,
                                            p["time_header_coord"])

            # only clean if the value is expected to be a time value
            if cls._must_be_time_value(curr_time, next_time, last_time):

                try:
                    curr_time = cls._parse_time(params, curr_time, last_time,
                                                next_time)

                    # correct typos checking for a healthy time progression
                    curr_time = cls._correct_progression(last_time,
                                                         curr_time,
                                                         p["frequency"],
                                                         p["missings"],
                                                         p["missing_value"])

                    # write the clean value to the spreadsheet
                    ws.cell(row=row, column=col).value = curr_time.datetime
                    last_time = curr_time

                # this is the only case that _must_be_time_value is not
                # expected to avoid before calling _parse_time, it's a mistake
                # of the excel designers in the time index
                except (DayOutOfRange, MonthOutOfRange):
                    ws.cell(row=row, column=col).value = None

    # PRIVATE auxiliar methods
    @classmethod
    def _must_be_time_value(cls, value, next_time, last_time):
        return (value is not None) and (len(unicode(value).strip()) > 0)

    @classmethod
    def _parse_time(cls, params, curr_time, last_time=None, next_time=None):
        """Try to parse any value into a proper date format.

        Iterate a pool of strategies looking one that understands the format of
        the time value to be parsed and declares to be able to parse it into
        a date format.

        Args:
            params: Parameters of the series being analyzed.
            curr_time: Value to be parsed into a date format.
            last_time: Last value parsed into time value.
            next_time: Next value to be parsed into time value.

        Returns:
            An arrow.Arrow object expressing a date.
        """

        for strategy in parse_time_strategies.get_strategies():
            if strategy.accepts(params, curr_time, last_time, next_time):
                time_value = strategy.parse_time(params, curr_time, last_time,
                                                 next_time)

                msg = "parse_time strategies must assure a valid time value!"
                assert type(time_value) == arrow.Arrow, msg

                return time_value

        raise ParseTimeImplementationError(curr_time, last_time, next_time,
                                           params)

    @classmethod
    def _correct_progression(cls, last_time, curr_time,
                             freq, missings, missing_value=None):

        # without a last_time the progression cannot be corrected
        if not last_time:
            return curr_time

        exp_time = increment_time(last_time, 1, freq)
        assert type(exp_time) == arrow.Arrow
        assert type(last_time) == arrow.Arrow or not last_time
        assert type(curr_time) == arrow.Arrow

        # everything is ok!
        if exp_time == curr_time:
            return curr_time

        # going back
        if curr_time < last_time:
            if cls._time_value_typo(curr_time, exp_time):
                return exp_time
            else:
                raise TimeValueGoingBackwards(curr_time, exp_time,
                                              last_time)

        # going forth with no missings allowed
        going_forth = curr_time > last_time
        if going_forth and not missings:
            if cls._time_value_typo(curr_time, exp_time):
                return exp_time
            else:
                raise TimeValueGoingForth(curr_time, exp_time,
                                          last_time)

        # going forth with implicit missings
        max_forth_time_value = increment_time(last_time,
                                              cls._max_forth_units(freq), freq)
        going_too_forth = curr_time > max_forth_time_value
        if going_too_forth and missings and missing_value == "Implicit":
            forth_time_value = cls._forth_time_value_typo(curr_time,
                                                          max_forth_time_value)
            if forth_time_value:
                return forth_time_value
            else:
                return False

        # everything should be ok
        else:
            return curr_time

    @classmethod
    def _max_forth_units(cls, freq):
        max_forth_units = {"D": 20,
                           "M": 2,
                           "Q": 1,
                           "Y": 1}
        if freq in max_forth_units:
            return max_forth_units[freq]
        else:
            return max(max_forth_units.values())

    @classmethod
    def _time_value_typo(cls, curr_time, exp_time):
        """Check if a time value could have a human typo.

        It relies in the idea that if the current time value being
        parsed is equal in two of the three parameters of a date
        (day, month and year), the different one is a human typo.

        Args:
            curr_time: Time value to be analyzed for a typo.
            exp_time: Expected time value to compare.
        """

        matches = [(curr_time.day == exp_time.day),
                   (curr_time.month == exp_time.month),
                   (curr_time.year == exp_time.year)]

        if matches.count(True) == 2:
            return True
        else:
            return False

    @classmethod
    def _forth_time_value_typo(cls, curr_time, max_forth_time_value):
        """Check for a typo in day, month or year.

        This check is based on the idea that one of the three elements of
        the date is wrong because of a typo that makes the date greater than a
        possible maximum. When one of the possibilities generates a date lower
        than maximum it means the typo was succesfully corrected.

        Args:
            curr_time (arrow.Arrow): Time value being analyzed because
                it is greater than it should be.
            max_forth_time_value (arrow.Arrow): Maximum possible time value for
                curr_time being analyzed.

        Returns:
            arrow.Arrow or None: A fixed time value removing the typo or None
                if the typo couldn't be fixed.
        """

        day_typo = arrow.get(curr_time.year,
                             curr_time.month,
                             max_forth_time_value.day)

        month_typo = arrow.get(curr_time.year,
                               max_forth_time_value.month,
                               curr_time.day)

        year_typo = arrow.get(max_forth_time_value.year,
                              curr_time.month,
                              curr_time.day)

        for possible_typo in [day_typo, month_typo, year_typo]:
            if possible_typo < max_forth_time_value:
                return possible_typo

        return None


class BaseSingleColumn(BaseCleanTiStrategy):

    """Clean time indexes that use a single column."""

    # PRIVATE INTERFACE METHODS
    @classmethod
    def _accepts(cls, ws, params):
        return not params["time_multicolumn"]

    @classmethod
    def _get_time_write_col(cls, ws, time_header_coord):
        """Returns the column where clean time index shouls be written."""
        return column_index_from_string(ws[time_header_coord].column)

    @classmethod
    def _get_time_value(cls, ws, row, time_header_coord):
        """Returns the time value corresponding a certain series and row."""
        col = cls._get_time_write_col(ws, time_header_coord)
        return ws.cell(row=row, column=col).value


class BaseMultipleColumn(BaseCleanTiStrategy):

    """Clean time indexes that use a single column."""

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


class BaseOffsetTi(BaseCleanTiStrategy):

    """Clean time indexes where time alignment is offset, sharing the same
    column with the data."""

    @classmethod
    def _accepts(cls, ws, params):
        return params["time_alignment"] != 0

    @classmethod
    def _must_be_time_value(cls, value, next_time, last_time):
        base_cond = super(BaseOffsetTi, cls)._must_be_time_value(value)
        return base_cond and type(value) != float


class CleanSingleColumn(BaseSingleColumn):

    """Clean time indexes that use a single column, different than the one
    used by the datea and with no offset time alignment."""

    @classmethod
    def _accepts(cls, ws, params):
        base_cond = super(CleanSingleColumn, cls)._accepts(ws, params)
        return base_cond and params["time_alignment"] == 0


class CleanMultipleColumns(BaseMultipleColumn):

    """Clean time indexes that use multiple columns concatenating values."""

    @classmethod
    def _accepts(cls, ws, params):
        base_cond = super(CleanMultipleColumns, cls)._accepts(ws, params)
        return base_cond and params["time_alignment"] == 0


class CleanSingleColumnWithOffset(BaseSingleColumn, BaseOffsetTi):

    """Clean time indexes that use a single column, different than the one
    used by the datea and with no offset time alignment."""

    @classmethod
    def _accepts(cls, ws, params):
        single_cond = BaseSingleColumn._accepts(ws, params)
        offset_cond = BaseOffsetTi._accepts(ws, params)
        return single_cond and offset_cond


def get_strategies():
    return xlseries.utils.strategies_helpers.get_strategies()

if __name__ == '__main__':
    pprint(sorted(xlseries.utils.strategies_helpers.get_strategies_names()))
