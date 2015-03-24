#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
time_utils
----------------------------------

Small useful time related methods.
"""

import datetime


def increment_time(time, num, freq):
    """Return time incremented in "num" times "frequency"."""

    freq_to_time_delta = {"S": "seconds",
                          "T": "minutes",
                          "H": "hours",
                          "D": "days",
                          "W": "weeks",
                          "M": "months",  # not a valid timedelta key
                          "Q": "quarters",  # not a valid timedelta key
                          "Y": "years"}  # not a valid timedelta key

    if freq in freq_to_time_delta:

        if freq not in ["M", "Q", "Y"]:
            time_delta_key = freq_to_time_delta[freq]
            time_delta_dict = {time_delta_key: num}
            time_delta = datetime.timedelta(**time_delta_dict)
            new_time = time + time_delta

        else:
            if freq == "M":
                new_time = _increment_months(time, num)
            elif freq == "Q":
                new_time = _increment_months(time, num * 3)
            elif freq == "Y":
                new_time = _increment_years(time, num)
            else:
                raise Exception("Unknown frequency")

    else:
        new_time = None

    return new_time


def _increment_months(time, num):

    msg = "No time object: " + str(time)
    assert type(time) == datetime.datetime, msg

    month = time.month
    for increment in xrange(num):
        if month == 12:
            month = 1
        else:
            month += 1

    year = time.year + int(num / 12) + int((num % 12 + time.month) / 12)

    return datetime.datetime(year, month, time.day)


def _increment_years(time, num):
    return datetime.datetime(time.year + num, time.month, time.day)
