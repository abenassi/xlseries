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
import datetime
import inspect
from pprint import pprint
from openpyxl.cell import column_index_from_string
from xlseries.utils.time import increment_time


class BaseCleanTiStrategy(object):

    """BaseCleanTiStrategy class for all time index cleaning strategies."""

    MAX_IMPL = 7

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
        if not exp_time_value:
            msg = "No expected time value could be calcualted from " + \
                str(last_time_value) + " " + str(freq)
            raise Exception(msg)

        # everything is ok!
        if exp_time_value == curr_time_value:
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

        day_typo = datetime.datetime(year=curr_time_value.year,
                                     month=curr_time_value.month,
                                     day=max_forth_time_value.day)

        month_typo = datetime.datetime(year=curr_time_value.year,
                                       month=max_forth_time_value.month,
                                       day=curr_time_value.day)

        year_typo = datetime.datetime(year=max_forth_time_value.year,
                                      month=curr_time_value.month,
                                      day=curr_time_value.day)

        for possible_typo in [day_typo, month_typo, year_typo]:
            if possible_typo < max_forth_time_value:
                return possible_typo

        return None


class BaseCleanSingleColumnTi(BaseCleanTiStrategy):

    """Clean time indexes that use a single column."""

    # PRIVATE INTERFACE METHODS
    @classmethod
    def _accepts(cls, ws, params):
        return not params["time_multicolumn"]

    @classmethod
    def _clean_time_index(cls, ws, params):
        """Extract time data series and return them as data frames."""

        p = params
        status_index = True

        col = column_index_from_string(ws[p["time_header_coord"]].column)

        # iterate series time index values
        last_time = None
        for i_row in xrange(p["data_starts"], p["data_ends"] + 1):
            curr_time = ws.cell(row=i_row, column=col).value

            # clean curr time value, in case of format errors or no time values
            curr_time = cls._parse_time(curr_time, p["time_format"], last_time)

            if curr_time:

                # correct date typos checking a healthy time progression
                new_time = None
                if curr_time and last_time:
                    new_time = cls._correct_progression(last_time,
                                                        curr_time,
                                                        p["frequency"],
                                                        p["missings"],
                                                        p["missing_value"])

                    # write the clean value again in the file, if succesful
                    if new_time and type(new_time) == p["time_format"]:
                        ws.cell(row=i_row, column=col).value = new_time
                        last_time = copy.deepcopy(new_time)

                    # value needs to be corected, attempt was unsuccesful
                    else:
                        status_index = False

                if not new_time:
                    last_time = curr_time

        return status_index


class CleanSimpleTi(BaseCleanSingleColumnTi):

    """Clean simple time indexes in a format very close to a datetime obj."""

    # PRIVATE INTERFACE METHODS
    @classmethod
    def _accepts(cls, ws, params):
        return not params["time_multicolumn"] and not params["time_composed"]

    @classmethod
    def _parse_time(cls, value, time_format, *args, **kwargs):

        # time format is correct
        if type(value) == time_format:
            time_value = value

        # fix strings time formats
        elif type(value) == str or type(value) == unicode:
            str_value = value.replace(".", "-").replace("/", "-")
            str_format = "%d-%m-%y"
            time_value = datetime.datetime.strptime(str_value, str_format)

        # no time could be parsed from the value
        else:
            time_value = None

        return time_value


class CleanComposedTi(BaseCleanTiStrategy):

    """Clean simple time indexes in a format very close to a datetime obj."""

    # PRIVATE INTERFACE METHODS
    @classmethod
    def _accepts(cls, ws, params):
        return not params["time_multicolumn"] and params["time_composed"]

    @classmethod
    def _parse_time(cls, value, time_format, last_time, *args, **kwargs):

        # time format is correct
        if type(value) == time_format:
            time_value = value

        # fix strings time formats
        elif type(value) == str or type(value) == unicode:
            str_value = value.replace(".", "-").replace("/", "-")
            str_format = "%d-%m-%y"
            time_value = datetime.datetime.strptime(str_value, str_format)

        # no time could be parsed from the value
        else:
            time_value = None

        return time_value


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
