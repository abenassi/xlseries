#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_comparing
----------------------------------

Tests for `comparing` utils module.
"""

from __future__ import unicode_literals
import unittest
import nose
import numpy as np

from xlseries.utils.comparing import approx_equal, compare_list_values


class ComparingTest(unittest.TestCase):

    def test_approx_equal(self):
        self.assertTrue(approx_equal(10, 10, 0.01))
        self.assertFalse(approx_equal(10, 10.1, 0.009))
        self.assertTrue(approx_equal(None, None))
        self.assertTrue(approx_equal(np.NaN, np.NaN))
        self.assertTrue(approx_equal("a", "a"))
        self.assertFalse(approx_equal("a", "b"))

    def test_list_values(self):
        self.assertTrue(
            compare_list_values([10, 20, 30],
                                [10, 20, 30]))
        self.assertTrue(
            compare_list_values([10, 20, 30],
                                [9.999, 19.999, 29.999]))
        self.assertFalse(
            compare_list_values([10, 20, 30],
                                [9.998, 19.998, 29.998]))

if __name__ == '__main__':
    # nose.main()
    nose.run(defaultTest=__name__)
