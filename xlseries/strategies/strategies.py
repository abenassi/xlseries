#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
strategies
----------------------------------

This module contains the high level strategies used by `xlseries` to parse
time data series inside excel files into Pandas DataFrames.
"""

import sys
import inspect
from pprint import pprint
import pandas as pd
import numpy as np
from openpyxl.cell import column_index_from_string

from xlseries.strategies.discover.parameters import Parameters
import xlseries.strategies.clean.time_index as clean_ti_strategies
import xlseries.strategies.get.data as get_data_strategies


# EXCEPTIONS
class TimeIndexNotClean(Exception):

    """Raised if time index of a worksheet could not be cleaned."""
    pass


# STRATEGIES
class BaseStrategy(object):

    """BaseStrategy class for higher level strategies.

    Attributes:
        wb: An openpyxl workbook loaded with "data_only=True" parameter.
        input_params: An optional attribute with parameters ready to be used
            in parsing wb. If not passed, the strategy will have to discover
            them or adopt a different approach to parse wb.
    """

    def __init__(self, wb, params_path=None):
        self.wb = wb
        self.params = Parameters(params_path)

    # PUBLIC INTERFACE
    @classmethod
    def accepts(cls, wb):
        return cls._accepts(wb)

    def get_data_frames(self):
        return self._get_data_frames()


class ParameterDiscovery(BaseStrategy):

    """Strategy that aims to discover key parsing parameters."""

    # PRIVATE INTERFACE METHODS
    @classmethod
    def _accepts(cls, wb):
        return True

    def _get_data_frames(self):
        """Extract time data series and return them as data frames."""

        ws = self.wb.active

        # First: discover the parameters of the file
        self._discover_parameters(ws)

        # Second: clean the data
        self._clean_data(ws)

        # Third: get the date from a cleaned worksheet
        return self._get_data(ws)

    # HIGH LEVEL TASKS
    def _discover_parameters(self, ws):
        """Discover the parameters of the worksheet."""
        pass

    def _clean_data(self, ws):
        """Ensure data is clean to be processed with the parameters."""

        # 1. Clean time index
        for i_series in xrange(len(self.params.time_header_coord)):
            self._clean_time_index(ws, self.params[i_series])

        # 2. Clean data values
        for i_series in xrange(len(self.params.headers_coord)):
            self._clean_values(ws)

    def _get_data(self, ws):
        """Parse data using parameters and return it in data frames."""

        # 1. Build data frames dict based on amount of period ranges founded
        dfs_dict = {}
        for period_range in self._get_period_ranges(ws):
            hashable_pr = self._hash_period_range(period_range)
            if hashable_pr not in dfs_dict:
                dfs_dict[hashable_pr] = {"columns": [], "data": [],
                                         "period_range": period_range}

        # 2. Get name (column) and values of each data series
        for i_series in xrange(len(self.params.headers_coord)):

            # iterate strategies looking for someone that accepts it
            params = self.params[i_series]
            name, values = None, None
            for strategy in get_data_strategies.get_strategies():
                if strategy.accepts(ws, params):
                    strategy_obj = strategy()
                    name, values = strategy_obj.get_data(ws, params)
                    break

            # raise exception if no strategy accepts the input
            if not name or not values:
                msg = "There is no strategy to deal with " + str(params)
                raise Exception(msg)

            # print "period range", params["frequency"], params["data_starts"], params["headers_coord"], params["data_ends"], params["time_alignment"]
            period_range = self._get_period_range(ws, params["frequency"],
                                                  params["data_starts"],
                                                  params["time_header_coord"],
                                                  params["data_ends"],
                                                  params["time_alignment"])
            hashable_pr = self._hash_period_range(period_range)

            dfs_dict[hashable_pr]["columns"].append(name)
            dfs_dict[hashable_pr]["data"].append(values)

        # 3. Build data frames
        dfs = []
        for df_inputs in dfs_dict.values():

            period_range = df_inputs["period_range"]
            columns = df_inputs["columns"]
            data = np.array(df_inputs["data"]).transpose()

            df = pd.DataFrame(index=period_range,
                              columns=columns,
                              data=data)

            dfs.append(df)

        return dfs

    @staticmethod
    def _hash_period_range(period_range):
        """Returns a tuple describing a period range in a hashable way."""
        return period_range.freqstr, period_range[0], period_range[-1]

    # 2. CLEAN DATA methods
    @classmethod
    def _clean_time_index(cls, ws, params):
        """This is changing ws..."""

        # raise Exception(ws.title + unicode(params) + " accepted!")
        # raise Exception(clean_ti_strategies.get_strategies())

        for strategy in clean_ti_strategies.get_strategies():
            # print strategy
            if strategy.accepts(ws, params):
                strategy_obj = strategy()
                strategy_obj.clean_time_index(ws, params)
                return

        msg = "Time index in '" + ws.title + "'' could not be cleaned."
        raise TimeIndexNotClean(msg)

    @classmethod
    def _clean_values(cls, ws):
        status_values = True

        return status_values

    # 3. GET DATA methods
    def _get_period_ranges(self, ws):
        """Get period ranges for all series in the worksheet.

        Args:
            ws: A clean worksheet with time data series.
        """

        period_ranges = []

        for freq, ini_row, header_coord, end_row, time_alignement in \
            zip(self.params.frequency, self.params.data_starts,
                self.params.time_header_coord, self.params.data_ends,
                self.params.time_alignment):

            pr = self._get_period_range(ws, freq, ini_row, header_coord,
                                        end_row, time_alignement)
            period_ranges.append(pr)

        return period_ranges

    def _get_period_range(self, ws, freq, ini_row, header_coord, end_row,
                          time_alignement):

        col = column_index_from_string(ws[header_coord].column)
        start = ws.cell(row=ini_row + time_alignement, column=col).value
        end = ws.cell(row=end_row + time_alignement, column=col).value

        # print start, end, freq
        period_range = pd.period_range(start, end, freq=freq)

        return period_range


def get_strategies_names():
    """Returns a list of the parsers names, whith no Base classes."""

    list_cls_tuple = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    list_cls_names = [cls_tuple[0] for cls_tuple in list_cls_tuple]
    list_no_base_cls_names = [cls_name for cls_name in list_cls_names
                              if cls_name[:4] != "Base" and
                              cls_name != "Parameters" and
                              cls_name != "TimeIndexNotClean"]

    return list_no_base_cls_names


def get_strategies():
    """Returns a list of references to the parsers classes."""

    return [globals()[cls_name] for cls_name in get_strategies_names()]


if __name__ == '__main__':
    pprint(sorted(get_strategies_names()))
