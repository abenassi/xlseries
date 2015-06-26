#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
xlseries

Main module to parse time data series inside excel files into Pandas
DataFrames. This is the only module that the user should use.
"""

from openpyxl import load_workbook, Workbook
from strategies import strategies


class XlSeries(object):

    """Time data series parser for excel files.

    Attributes:
        wb: Workbook object. The user can either pass the path where the excel
            file is loated or the Workbook object with the xl already loaded.
    """

    def __init__(self, xl_path_or_wb):
        if type(xl_path_or_wb) == Workbook:
            self.wb = xl_path_or_wb

        else:
            self.wb = load_workbook(xl_path_or_wb, data_only=True)

    # PUBLIC
    def get_data_frames(self, params_path_or_obj, safe_mode=False):
        """Returns pandas data frames of time series found in the xl file.

        Args:
            params_path_or_obj (str or Parameters): Path to a json file with
                parameters to parse the excel file.
            safe_mode (bool): When some parameters are not passed by the user,
                the safe mode will check all possible combinations, returning
                more than one result if many are found. If safe_mode is set to
                False, the first succesful result will be returned without
                checking the other possible combinations of parameters.
        """

        for strategy in strategies.get_strategies():
            if strategy.accepts(self.wb):
                strategy_obj = strategy(self.wb, params_path_or_obj)
                return strategy_obj.get_data_frames()
