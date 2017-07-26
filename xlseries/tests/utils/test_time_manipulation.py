#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_time_manipulation
----------------------------------

Tests for `time_manipulation` module.
"""

import arrow
import unittest
import nose
from xlseries.utils.time_manipulation import increment_time
from xlseries.utils.time_manipulation import InvalidTimeFrequency
from xlseries.utils.time_manipulation import infer_freq


class TimeManipulationTest(unittest.TestCase):

    def test_increment_time(self):
        time = arrow.get(2015, 12, 1)

        new_time = increment_time(time, 1, "S")
        exp_new_time = arrow.get(2015, 12, 1, 0, 0, 1)
        self.assertEqual(new_time, exp_new_time)

        new_time = increment_time(time, 1, "D")
        exp_new_time = arrow.get(2015, 12, 2)
        self.assertEqual(new_time, exp_new_time)

        new_time = increment_time(time, 1, "M")
        exp_new_time = arrow.get(2016, 1, 1)
        self.assertEqual(new_time, exp_new_time)

        new_time = increment_time(time, 1, "Q")
        exp_new_time = arrow.get(2016, 3, 1)
        self.assertEqual(new_time, exp_new_time)

        new_time = increment_time(time, 1, "A")
        exp_new_time = arrow.get(2016, 12, 1)
        self.assertEqual(new_time, exp_new_time)

    def test_increment_time_exception(self):
        with self.assertRaises(InvalidTimeFrequency):
            time = arrow.get(2015, 2, 15)
            increment_time(time, 4, "X")

    def test_infer_freq(self):

        freq_exp = "MS"
        freq = infer_freq(2618767)
        self.assertEqual(freq, freq_exp)


if __name__ == '__main__':
    nose.run(defaultTest=__name__)
