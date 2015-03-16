#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
strategies
----------------------------------

This module contains the hight level strategies used by `xlseries` to parse
time data series inside excel files into Pandas DataFrames.
"""

import os
from pprint import pprint
import pyclbr
import pandas as pd
import numpy as np
from parameters import Parameters
from utils import get_data_frames
from openpyxl.cell import coordinate_from_string, column_index_from_string


class BaseStrategy(object):

    """BaseStrategy class for all strategies."""

    def __init__(self, wb, input_params=Parameters()):
        self.wb = wb
        self.params = input_params

    # PUBLIC INTERFACE
    @classmethod
    def accepts(cls, wb):
        return cls._accepts(wb)

    def get_data_frames(self):
        return self._get_data_frames()


class ParameterDiscovery(BaseStrategy):

    """Strategy that aims to discover key parsing parameters."""

    @classmethod
    def _accepts(cls, wb):
        return True

    def _get_data_frames(self):

        # First you should discover the parameters
        # ...

        # When you know the parameters, is simple (is simple?)

        ws = self.wb.active

        # build period ranges
        period_ranges = self._get_period_ranges(ws)

        # build frames dict based on amount of frequencies
        frames_input_dict = {}
        for freq in self.params.frequency:
            frames_input_dict[freq] = {"columns": [], "data": []}

        # get name and data of each data series
        for header_coord, freq, ini_row, end_row in \
            zip(self.params.headers_coord, self.params.frequency,
                self.params.data_starts, self.params.data_ends):

            columns = frames_input_dict[freq]["columns"]
            data = frames_input_dict[freq]["data"]

            name = self._get_name(ws, header_coord)
            columns.append(name)

            values = self._get_values(ws, header_coord, ini_row, end_row)
            data.append(values)

        # build data frames
        dfs = []
        for period_range in period_ranges:
            columns = frames_input_dict[period_range.freqstr]["columns"]
            data = frames_input_dict[period_range.freqstr]["data"]
            np_data = np.array(data).transpose()

            df = pd.DataFrame(index=period_range,
                              columns=columns,
                              data=np_data)

            dfs.append(df)

        return dfs

    def _get_period_ranges(self, ws):

        period_ranges = []

        for freq, ini_row, header_coord, end_row, time_alignement in \
            zip(self.params.frequency, self.params.data_starts,
                self.params.time_header_coord, self.params.data_ends,
                self.params.time_alignement):

            pr = self._get_period_range(ws, freq, ini_row, header_coord,
                                        end_row, time_alignement)
            period_ranges.append(pr)

        return period_ranges

    def _get_period_range(self, ws, freq, ini_row, header_coord, end_row,
                          time_alignement):
        col = column_index_from_string(ws[header_coord].column)
        period_range = pd.period_range(ws.cell(row=ini_row + time_alignement,
                                               column=col).value,
                                       ws.cell(row=end_row + time_alignement,
                                               column=col).value,
                                       freq=freq)

        return period_range

    def _get_name(self, ws, header_coord):
        return ws[header_coord].value

    def _get_values(self, ws, header_coord, ini_row, end_row):
        # TODO: Rework this method to manage interrupted series
        col = column_index_from_string(ws[header_coord].column)

        values = []
        i_row = ini_row
        while i_row <= end_row:
            value = ws.cell(row=i_row, column=col).value
            if value:
                values.append(float(value))
            else:
                values.append(np.nan)

            i_row += 1

        return values


def get_parsers_names():
    """Returns a list of the parsers names, whith no Base classes."""

    name = os.path.splitext(os.path.basename(__file__))[0]
    list_cls_names = (pyclbr.readmodule(name).keys())
    list_no_base_cls_names = [cls_name for cls_name in list_cls_names
                              if cls_name[:4] != "Base"]

    return list_no_base_cls_names


def get_parsers():
    """Returns a list of references to the parsers classes."""

    return [globals()[cls_name] for cls_name in get_parsers_names()]


if __name__ == '__main__':
    pprint(sorted(get_parsers_names()))
