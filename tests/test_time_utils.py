#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_time_utils
----------------------------------

Tests for `time_utils` module.
"""

import datetime
import unittest
import nose
from xlseries.time_utils import increment_time


class TimeUtilsTest(unittest.TestCase):

    def test_increment_time(self):
        time = datetime.datetime(2015, 12, 1)

        new_time = increment_time(time, 1, "S")
        exp_new_time = datetime.datetime(2015, 12, 1, 0, 0, 1)
        self.assertEqual(new_time, exp_new_time)

        new_time = increment_time(time, 1, "D")
        exp_new_time = datetime.datetime(2015, 12, 2)
        self.assertEqual(new_time, exp_new_time)

        new_time = increment_time(time, 1, "M")
        exp_new_time = datetime.datetime(2016, 1, 1)
        self.assertEqual(new_time, exp_new_time)

        new_time = increment_time(time, 1, "Q")
        exp_new_time = datetime.datetime(2016, 3, 1)
        self.assertEqual(new_time, exp_new_time)

        new_time = increment_time(time, 1, "Y")
        exp_new_time = datetime.datetime(2016, 12, 1)
        self.assertEqual(new_time, exp_new_time)


if __name__ == '__main__':
    nose.run(defaultTest=__name__)
