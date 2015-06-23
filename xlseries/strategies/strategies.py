#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
strategies

This module contains the high level strategies used by `xlseries` to parse
time data series inside excel files into Pandas DataFrames.
"""

import sys
import inspect
from pprint import pprint
import pandas as pd
import numpy as np
from openpyxl.cell import column_index_from_string

import xlseries.utils.strategies_helpers
from xlseries.strategies.discover.parameters import Parameters
import xlseries.strategies.clean.time_index as clean_ti_strategies
import xlseries.strategies.get.data as get_data_strategies
import xlseries.strategies.get.period_range as get_pr_strategies


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

    def __init__(self, wb, params_path_or_obj=None):
        self.wb = wb

        if type(params_path_or_obj) == Parameters:
            self.params = params_path_or_obj
        else:
            self.params = Parameters(params_path_or_obj)
        # raise Exception(self.params)

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

        # if time index is multicolumn, only one time index is allowed
        if self.params["time_multicolumn"][0]:
            self._clean_time_index(ws, self.params[0])

        # if time index is not multicolumn, many time indexes are allowed
        else:
            time_indexes = set()
            for i_series in xrange(len(self.params.time_header_coord)):
                # avoid cleaning the same time index twice
                time_header_coord = self.params["time_header_coord"][i_series]
                if time_header_coord not in time_indexes:
                    time_indexes.add(time_header_coord)
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
                # print strategy, "is being asked.."
                if strategy.accepts(ws, params):
                    # print "accepted!"
                    strategy_obj = strategy()
                    names_and_values = strategy_obj.get_data(ws, params)
                    # print names_and_values
                    break

            # raise exception if no strategy accepts the input
            if not names_and_values:
                msg = "There is no strategy to deal with " + str(params)
                raise Exception(msg)

            prs = self._get_series_prs(ws, params["frequency"],
                                       params["data_starts"],
                                       params["time_header_coord"],
                                       params["data_ends"],
                                       params["time_alignment"],
                                       params["alignment"])

            for period_range, (name, values) in zip(prs, names_and_values):
                # print period_range, name, values
                hashable_pr = self._hash_period_range(period_range)

                self._add_name(name, dfs_dict[hashable_pr]["columns"])
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

    # auxiliar methods
    @staticmethod
    def _hash_period_range(period_range):
        """Returns a tuple describing a period range in a hashable way."""
        return period_range.freqstr, period_range[0], period_range[-1]

    # 2. CLEAN DATA methods
    @classmethod
    def _clean_time_index(cls, ws, params):
        """This is changing ws..."""

        for strategy in clean_ti_strategies.get_strategies():
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

        for (freq, ini_row, time_header_coord, end_row, time_alignement,
             alignment) in \
            zip(self.params.frequency, self.params.data_starts,
                self.params.time_header_coord, self.params.data_ends,
                self.params.time_alignment, self.params.alignment):

            for pr in self._get_series_prs(ws, freq, ini_row,
                                           time_header_coord,
                                           end_row, time_alignement,
                                           alignment):
                yield pr

    def _get_series_prs(self, ws, freq, ini_row, time_header_coord, end_row,
                        time_alignement, alignment):

        for strategy in get_pr_strategies.get_strategies():
            if strategy.accepts(ws, freq):
                return strategy.get_period_ranges(ws, freq, ini_row,
                                                  time_header_coord, end_row,
                                                  time_alignement,
                                                  alignment)

        msg = " ".join(["There is no strategy to get period range for",
                        "\nFrequency:", freq,
                        "\nTime header coord:", time_header_coord])
        raise Exception(msg)

    def _add_name(self, name, columns, index=1):
        if self._indexed_name(name, index) not in columns:
            columns.append(self._indexed_name(name, index))
        else:
            self._add_name(name, columns, index + 1)

    def _indexed_name(self, name, index):
        if index <= 1:
            return name
        else:
            return name + "." + unicode(index)



def get_strategies():
    return xlseries.utils.strategies_helpers.get_strategies()

if __name__ == '__main__':
    pprint(sorted(xlseries.utils.strategies_helpers.get_strategies_names()))
