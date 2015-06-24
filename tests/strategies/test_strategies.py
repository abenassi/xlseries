#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_strategies

Tests for `strategies` module.
"""

from __future__ import unicode_literals
import unittest
import nose
import pandas as pd
from functools import wraps

from xlseries.utils.case_loaders import load_original_case
from xlseries.utils.case_loaders import load_parameters_case
from xlseries.utils.case_loaders import load_expected_case
from xlseries.utils.data_frame import compare_period_ranges
from xlseries.utils.data_frame import compare_data_frames
from xlseries.strategies.strategies import ParameterDiscovery


# @unittest.skip("skip")
class ParameterDiscoveryTestCase(unittest.TestCase):

    # @unittest.skip("skip")
    def test_get_period_ranges(self):

        test_wb = load_original_case(2)
        params = load_parameters_case(2)
        strategy_obj = ParameterDiscovery(test_wb, params)
        ws = strategy_obj.wb.active

        pr_d = pd.period_range("20020304", "20140410", freq="D")
        pr_m = pd.period_range("20020301", "20140301", freq="M")

        period_ranges = list(strategy_obj._get_period_ranges(ws, params))

        self.assertTrue(compare_period_ranges(pr_d, period_ranges[0]))
        self.assertTrue(compare_period_ranges(pr_m, period_ranges[1]))

    def test_parameters_are_complete(self):
        pass



if __name__ == '__main__':
    # unittest.main()
    nose.run(defaultTest=__name__)
