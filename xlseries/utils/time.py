#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
time_utils
----------------------------------

Small useful time related methods.
"""

import arrow
import datetime


def increment_time(time, num, freq):
    """Return time incremented in "num" times "frequency".

    Args:
        time: Time to increment.
        num: Number of time units to shift from time.
        freq: Type or frequency of time units.
    """
    # check correct time type
    if type(time) == datetime.datetime:
        time = arrow.get(time)

    freqs = {"S": "seconds",
             "T": "minutes",
             "H": "hours",
             "D": "days",
             "W": "weeks",
             "M": "months",
             "Q": "quarters",  # not a valid timedelta key
             "Y": "years"}

    # calculate shifted time if frequency is valid
    if freq in freqs:
        if freq != "Q":
            replace = {freqs[freq]: num}
        else:
            replace = {"months": num * 3}

        shifted_time = time.replace(**replace)

    else:
        shifted_time = None

    return shifted_time
