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

        # When you know the parameters, is simple
        ws = self.wb.active
        period_range = self._get_period_range(ws)
        columns = []
        data = []
        for header_coord in self.params.headers_coord:

            name = self._get_name(ws, header_coord)
            columns.append(name)

            values = self._get_values(ws, header_coord)
            data.append(values)
            # print "Got here"

        np_data = np.array(data).transpose()

        df = pd.DataFrame(index=period_range,
                          columns=columns,
                          data=np_data)

        dfs = [df]

        return dfs

    def _get_period_range(self, ws):
        ini_row = self.params.data_starts
        header_coord = self.params.time_header_coord
        col = column_index_from_string(ws[header_coord].column)
        end_row = self.params.data_ends

        period_range = pd.period_range(ws.cell(row=ini_row, column=col).value,
                                       ws.cell(row=end_row, column=col).value,
                                       freq=self.params.frequency)

        return period_range

    def _get_name(self, ws, header_coord):
        return ws[header_coord].value

    def _get_values(self, ws, header_coord):
        ini_row = self.params.data_starts
        col = column_index_from_string(ws[header_coord].column)
        end_row = self.params.data_ends

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
