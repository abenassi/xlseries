# -*- coding: utf-8 -*-

from openpyxl import load_workbook
from xlseries import strategies
from xlseries import evaluation


class XlSeries(object):

    """Time data series parser for excel files."""

    def __init__(self, xl_name):
        self.wb = load_workbook(xl_name)

    # PUBLIC
    def get_data_frames(self, all_results=True):
        """Returns pandas data frames of time series found in the xl file.

        Args:
            all_results: If True all results are returned ordered by evaluation
                result. Otherwise only the best result is returned.
        """

        results = []

        for strategy in strategies.main.get_strategies():
            if strategy.accepts(self.wb):

                result = strategy(self.wb).get_data_frames()
                eval_result = evaluation.evaluate(result)
                results.append((eval_result, result))

        sorted_results = sorted(results, key=lambda x: x[0])

        if all_results:
            return sorted_results

        else:
            return sorted_results[0]
