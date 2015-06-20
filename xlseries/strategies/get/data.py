#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
data

This module contains strategies to get data from a spreadsheet.
"""

from __future__ import unicode_literals
import sys
import inspect
from pprint import pprint
import arrow
import datetime
import numpy as np
from openpyxl.cell import column_index_from_string
from unidecode import unidecode

from xlseries.utils.time_manipulation import increment_time


class BaseGetDataStrategy(object):

    """BaseGetDataStrategy class for all get data strategies."""

    # PUBLIC INTERFACE
    @classmethod
    def accepts(cls, ws, params):
        return cls._accepts(ws, params)

    @classmethod
    def get_data(cls, ws, params):
        return cls._get_data(ws, params)


class BaseGetSingleFrequencyData(BaseGetDataStrategy):

    @classmethod
    def _accepts(cls, ws, params):
        return not params["multifrequency"]

    @classmethod
    def _get_data(cls, ws, params):
        name = cls._get_name(ws, params["headers_coord"])
        values = cls._get_values(ws, params)

        return [(name, values)]

    # PRIVATE
    @classmethod
    def _get_name(cls, ws, header_coord):
        return unidecode(ws[header_coord].value)

    @classmethod
    def _get_values(cls, ws, params):
        col = column_index_from_string(ws[params["headers_coord"]].column)

        values = []
        i_row = params["data_starts"]
        while i_row <= params["data_ends"]:
            value = ws.cell(row=i_row, column=col).value

            new_value = cls._handle_new_value(values, value,
                                              params["continuity"],
                                              params["missings"],
                                              params["missing_value"])

            if cls._value_to_be_added(new_value, i_row, ws, params):
                values.append(new_value)

            i_row += 1

        # fill the missing values if they are implicit
        if params["missings"] and params["missing_value"] == "Implicit":
            values = cls._fill_implicit_missings(ws, values,
                                                 params["frequency"],
                                                 params["time_header_coord"],
                                                 params["data_starts"],
                                                 params["data_ends"])

        return values

    @classmethod
    def _handle_new_value(cls, values, value, continuity, missings,
                          missing_value):

        new_value = None

        if continuity:
            if missings:
                if value != missing_value:
                    args_without_values = locals()
                    del args_without_values["values"]
                    try:
                        new_value = float(value)
                    except:
                        print args_without_values
                        raise Exception("Value is not valid " + unicode(value))
                else:
                    new_value = np.nan
            else:
                new_value = float(value)

        # handles non continuity
        else:
            if missings:
                if value == missing_value:
                    new_value = np.nan
                elif cls._valid_value(value):
                    new_value = float(value)
                # values that are not valid nor missings
                else:
                    pass
            else:
                if cls._valid_value(value):
                    new_value = float(value)

        return new_value

    @classmethod
    def _valid_value(cls, value):
        """Check if a value is likely to be a series data value."""

        RV = True

        try:
            float(value)
        except:
            RV = False

        return RV

    @classmethod
    def _fill_implicit_missings(cls, ws, values, frequency, time_header_coord,
                                ini_row, end_row):
        """Fill time holes in the series with missing data."""

        col = ws[time_header_coord].column

        new_values = []
        ini_time_value = arrow.get(ws.cell(coordinate=col +
                                           unicode(ini_row)).value)
        exp_time_value = ini_time_value
        for row, (i_value, value) in zip(xrange(ini_row, end_row + 1),
                                         enumerate(values)):
            obs_time_value = arrow.get(
                ws.cell(coordinate=col + unicode(row)).value)

            # fill time holes in the series with missing data
            while exp_time_value < obs_time_value:
                new_values.append(np.nan)
                exp_time_value = increment_time(exp_time_value, 1, frequency)

            new_values.append(values[i_value])
            exp_time_value = increment_time(exp_time_value, 1, frequency)

        return new_values

    @classmethod
    def _value_to_be_added(cls, value, row, ws, params):
        """Check if a value should be added or not."""
        return value is not None


class GetSingleFrequencyDataContinuous(BaseGetSingleFrequencyData):

    """Get data with a single frequency and continous layout in a column."""

    @classmethod
    def _accepts(cls, ws, params):
        return (not params["multifrequency"] and params["continuity"])


class GetSingleFrequencyDataNotContinuous(BaseGetSingleFrequencyData):

    """Get data with a single frequency and data layout interrupted.

    The interruption is due to strange strings or values that should not be
    taken into account when gathering values. Series interrupted only by blank
    rows do not need this strategy."""

    @classmethod
    def _accepts(cls, ws, params):
        return (not params["multifrequency"] and not params["continuity"])

    @classmethod
    def _value_to_be_added(cls, value, row, ws, params):
        """Check if a value should be added or not.

        Value shouldn't be None and the row should correspond to a valid time
        value in the time index."""

        time_col = ws[params["time_header_coord"]].column
        time_coord = time_col + unicode(row + params["time_alignment"])
        time_value = ws[time_coord].value

        return value is not None and type(time_value) == datetime.datetime


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
