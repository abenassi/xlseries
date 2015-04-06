#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
clean_ti_strategies
----------------------------------

This module contains strategies to parse and clean time indexes in worksheets
cotaining time data series.
"""

import sys
import copy
import arrow
import inspect
from pprint import pprint
from openpyxl.cell import column_index_from_string

from xlseries.utils.time import increment_time
import xlseries.strategies.clean.parse_time as parse_time_strategies
from xlseries.strategies.clean.parse_time import ParseSimpleTime


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
        # print last_time_value, curr_time_value, exp_time_value, curr_time_value == exp_time_value, missing_value

        if not exp_time_value:
            msg = "No expected time value could be calcualted from " + \
                str(last_time_value) + " " + str(freq)
            raise Exception(msg)

        # everything is ok!
        if exp_time_value == curr_time_value:
            # print "ok!!"
            return curr_time_value

        # going back
        if curr_time_value < last_time_value:
            if cls._time_value_typo(curr_time_value, exp_time_value):
                return exp_time_value
            else:
                return False

        # going forth with no missings allowed
        going_forth = curr_time_value > last_time_value
        if going_forth and not missings:
            try:
                cls._time_value_typo(curr_time_value, exp_time_value)
            except Exception:
                print curr_time_value, exp_time_value, last_time_value

                if cls._time_value_typo(curr_time_value, exp_time_value):
                    return exp_time_value
            else:
                return False

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
        # print "here!"
        # print params
        time_value = None

        if curr_time:
            for strategy in parse_time_strategies.get_strategies():
                if strategy.accepts(curr_time, last_time, params):
                    # print strategy, "was accepted!"
                    time_value = strategy.parse_time(curr_time, last_time,
                                                         params)
                    break
        # time_value = ParseSimpleTime.parse_time(curr_time, last_time,
        #                                         params)
        # print time_value
        return time_value


class CleanSingleColumnTi(BaseCleanTiStrategy):

    """Clean time indexes that use a single column."""

    # PRIVATE INTERFACE METHODS
    @classmethod
    def _accepts(cls, ws, params):
        return not params["time_multicolumn"]

    @classmethod
    def _clean_time_index(cls, ws, params):
        """Extract time data series and return them as data frames."""
        # print "here"

        p = params
        # print p
        status_index = True

        col = column_index_from_string(ws[p["time_header_coord"]].column)

        # iterate series time index values
        last_time = None
        # print list(xrange(p["data_starts"], p["data_ends"] + 1))
        for i_row in xrange(p["data_starts"], p["data_ends"] + 1):
            curr_time = ws.cell(row=i_row, column=col).value

            # print type(curr_time)
            if curr_time:

                # clean curr time value, in case of format errors or no time values
                curr_time = cls._parse_time(curr_time, last_time, params)
                # print "1", curr_time, last_time

                # correct date typos checking a healthy time progression
                new_time = None
                if curr_time and last_time:
                    new_time = cls._correct_progression(last_time,
                                                        curr_time,
                                                        p["frequency"],
                                                        p["missings"],
                                                        p["missing_value"])

                    # write the clean value again in the file, if succesful
                    if new_time and type(new_time) == arrow.Arrow:
                        ws.cell(row=i_row, column=col).value = new_time.datetime
                        last_time = new_time
                        # print ws.cell(row=i_row, column=col).value

                    # value needs to be corected, attempt was unsuccesful
                    else:
                        status_index = False

                elif curr_time and not last_time:
                    ws.cell(row=i_row, column=col).value = curr_time.datetime

                if not new_time:
                    last_time = curr_time


        return status_index


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
    pprint(sorted(increment_time()))
