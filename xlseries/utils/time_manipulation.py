#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
time_manipulation

Small useful time related methods.
"""

import arrow
import datetime
from .comparing import approx_equal


class InvalidTimeFrequency(Exception):

    """Raised when the frequency passed isn't valid."""

    def __init__(self, time, frequency):
        msg = " ".join(["Frequency is invalid for incrementing time.\n",
                        "Time:", str(time),
                        "Frequency:", str(frequency)])
        super(InvalidTimeFrequency, self).__init__(msg)


def increment_time(time, num, freq):
    """Return time incremented in "num" times "frequency".

    Args:
        time: Time to increment.
        num: Number of time units to shift from time.
        freq: Type or frequency of time units.
    """
    # check correct time type
    if isinstance(time, datetime.datetime):
        time = arrow.get(time)

    freqs = {"S": "seconds",
             "T": "minutes",
             "H": "hours",
             "D": "days",
             "W": "weeks",
             "M": "months",
             "Q": "quarters",  # not a valid timedelta key
             "A": "years"}

    # calculate shifted time if frequency is valid
    if freq in freqs:
        if freq != "Q":
            replace = {freqs[freq]: num}
        else:
            replace = {"months": num * 3}

        shifted_time = time.replace(**replace)

    else:
        raise InvalidTimeFrequency(time, freq)

    return shifted_time


def infer_freq(av_seconds, tolerance=0.1):
    """Infer frequency of a time data series."""

    if approx_equal(1, av_seconds, tolerance):
        freq = 'S'
    elif approx_equal(60, av_seconds, tolerance):
        freq = 'T'
    elif approx_equal(3600, av_seconds, tolerance):
        freq = 'H'
    elif approx_equal(86400, av_seconds, tolerance):
        freq = 'D'
    elif approx_equal(604800, av_seconds, tolerance):
        freq = 'W'
    elif approx_equal(2419200, av_seconds, tolerance):
        freq = 'MS'
    elif approx_equal(7776000, av_seconds, tolerance):
        freq = 'QS'
    elif approx_equal(15552000, av_seconds, tolerance):
        raise Exception("Can't handle semesters!")
    elif approx_equal(31536000, av_seconds, tolerance):
        freq = 'AS'
    else:
        raise Exception("Average seconds don't match any frequency.")

    return freq
