#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
xlseries
----------------------------------

Main module to parse time data series inside excel files into Pandas
DataFrames. This is the only module that the user should use.
"""

from openpyxl import load_workbook
from evaluation import evaluation
from strategies import strategies


class XlSeries(object):

    """Time data series parser for excel files."""

    def __init__(self, xl_name):
        self.wb = load_workbook(xl_name)

    # PUBLIC
    def get_data_frames(self, all_results=True, params_path=None):
        """Returns pandas data frames of time series found in the xl file.

        Args:
            all_results: If True all results are returned ordered by evaluation
                result. Otherwise only the best result is returned. TODO: This
                feature is not implemented yet!!
            params_path: Path to a json file with parameters to parse the
                excel file.
        """

        results = []

        for strategy in strategies.get_strategies():

            if strategy.accepts(self.wb):
                strategy_obj = strategy(self.wb, params_path)
                strategy_results = strategy_obj.get_data_frames()
                # print "strat results", strategy_results

                for result in strategy_results:
                    eval_result = evaluation.evaluate(result)
                    results.append((eval_result, result))

        sorted_results = sorted(results, key=lambda x: x[0])

        if all_results:
            return sorted_results

        else:
            return sorted_results[0]
