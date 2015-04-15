#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
comparing
----------------------------------

Auxiliar methods to compare approximate values.
"""

from __future__ import unicode_literals
import numpy as np


def approx_equal(a, b, tolerance):
    """Check if a and b can be considered approximately equal."""

    RV = False

    if (not a) and (not b):
        RV = True

    elif np.isnan(a) and np.isnan(b):
        # print a, type(a), "not approx_equal to", b, type(b)
        RV = True

    elif a and (a != np.nan) and b and (b != np.nan):
        RV = _approx_equal(a, b, tolerance)

    else:
        RV = a == b

    return RV


def _approx_equal(a, b, tolerance):
    if abs(a - b) < tolerance * a:
        return True
    else:
        return False


def compare_list_values(values1, values2):
    """Check that all values of both lists are approximately equal."""

    RV = True

    for value1, value2 in zip(values1, values2):
        # print value1, value2, value2/value1-1
        if not approx_equal(value1, value2, 0.0001):
            RV = False
            break

    return RV
