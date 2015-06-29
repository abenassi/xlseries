#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
xlseries

Main module to parse time data series inside excel files into Pandas
DataFrames. This is the only module that the user should use in the normal use
case.
"""

from openpyxl import load_workbook, Workbook
from strategies import strategies
from utils.xl_methods import make_wb_copy

import warnings
warnings.filterwarnings("ignore")


class XlSeries(object):

    """Time data series parser for excel files.

    Attributes:
        wb: Workbook object. The user can either pass the path where the excel
            file is located or the Workbook object with the xl already loaded.
    """

    def __init__(self, xl_path_or_wb):
        """Args:
            xl_path_or_wb (str or Workbook): Path to an excel file or a
                Workbook object.
        """
        if type(xl_path_or_wb) == Workbook:
            self.wb = xl_path_or_wb
        else:
            self.wb = load_workbook(xl_path_or_wb, data_only=True)

    # PUBLIC
    def get_data_frames(self, params_path_or_obj, safe_mode=False):
        """Scrape time series from an excel file into a pandas.DataFrame.

        Args:
            params_path_or_obj (str, dict or Parameters): Parameters to scrape
                an excel file with time series:
                    dict: Python dictionary with parameters like
                        {"headers_coord": ["B1","C1"],
                         "data_starts": 2,
                         "frequency": "M",
                         "time_header_coord": "A1"}
                    str: Path to a JSON file with parameters.
                    Parameters: A Parameters object already built.
            safe_mode (bool): When some parameters are not passed by the user,
                the safe mode will check all possible combinations, returning
                more than one result if many are found. If safe_mode is set to
                False, the first succesful result will be returned without
                checking the other possible combinations of parameters.

        Returns:
            list: A list of pandas.DataFrame objects with time series scraped
                from the excel file. Every DataFrame in the list corresponds to
                a different frequency.
        """
        # wb will be changed, so it has to be a copy to preserve the original
        wb_copy = make_wb_copy(self.wb)

        for strategy in strategies.get_strategies():
            if strategy.accepts(wb_copy):
                strategy_obj = strategy(wb_copy, params_path_or_obj)
                return strategy_obj.get_data_frames(safe_mode)
