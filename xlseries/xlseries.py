# -*- coding: utf-8 -*-

from openpyxl import load_workbook


class XlSeries(object):

    """Time data series parser for excel files."""

    def __init__(self, xl_name):
        self.wb = load_workbook(xl_name)

    # PUBLIC
    def get_data_frame(self):
        """Returns a pandas data frame of time series found in the xl file."""
        pass
