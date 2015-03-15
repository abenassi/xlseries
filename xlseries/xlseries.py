#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
xlseries
----------------------------------

Main module to parse time data series inside excel files into Pandas
DataFrames. This is the only module that the user should use.
"""

from openpyxl import load_workbook
import strategies
import evaluation


class XlSeries(object):

    """Time data series parser for excel files."""

    def __init__(self, xl_name, ):
        self.wb = load_workbook(xl_name)

    # PUBLIC
    def get_data_frames(self, all_results=True, input_params=None):
        """Returns pandas data frames of time series found in the xl file.

        Args:
            all_results: If True all results are returned ordered by evaluation
                result. Otherwise only the best result is returned.
        """

        results = []

        for strategy in strategies.get_strategies():

            if strategy.accepts(self.wb):
                strategy_obj = strategy(self.wb, input_params)
                strategy_results = strategy_obj.get_data_frames()

                for result in strategy_results:
                    eval_result = evaluation.evaluate(result)
                    results.append((eval_result, result))

        sorted_results = sorted(results, key=lambda x: x[0])

        if all_results:
            return sorted_results

        else:
            return sorted_results[0]
