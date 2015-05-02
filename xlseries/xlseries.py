#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
xlseries
----------------------------------

Main module to parse time data series inside excel files into Pandas
DataFrames. This is the only module that the user should use.
"""

from openpyxl import load_workbook, Workbook
from evaluation import evaluation
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
            self.wb = load_workbook(xl_path_or_wb)

    # PUBLIC
    def get_data_frames(self, params_path_or_obj=None, all_results=True):
        """Returns pandas data frames of time series found in the xl file.

        Args:
            params_path_or_obj: Path to a json file with parameters to parse
                the excel file. It can also be the parameters object already
                loaded.
            all_results: If True all results are returned ordered by evaluation
                result. Otherwise only the best result is returned. TODO: This
                feature is not implemented yet!!
        """

        results = []

        for strategy in strategies.get_strategies():

            if strategy.accepts(self.wb):
                strategy_obj = strategy(self.wb, params_path_or_obj)
                strategy_results = strategy_obj.get_data_frames()
                # print "strat results", strategy_results

                for result in strategy_results:
                    # TODO: in the future the results will be evaluated and
                    # ordered by score, to compare similar results returned by
                    # different strategies, for now the loop just breaks after
                    # the first succesful strategy

                    # eval_result = evaluation.evaluate(result)
                    results.append(result)
                break

        return results
