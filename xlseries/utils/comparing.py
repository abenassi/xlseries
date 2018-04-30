#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
comparing

Auxiliar methods to compare approximate values.
"""

import numpy as np


def approx_equal(a, b, tolerance=0.00001):
    """Check if a and b can be considered approximately equal.

    Args:
        a: A float or int number.
        b: A float or int number.
        tolerance: Percentage of discrepancy allowed to be considered equal.

    Returns:
        True (a == b) or False (a != b)
    """

    RV = False

    if a == b:
        RV = True

    elif isinstance(a, str) and isinstance(b, str):
        RV = a == b

    elif (not a) and (not b):
        RV = True

    elif np.isnan(a) and np.isnan(b):
        # print a, type(a), "not approx_equal to", b, type(b)
        RV = True

    elif a and (a != np.nan) and b and (b != np.nan):
        RV = _approx_equal(a, b, tolerance)

    else:
        msg = " ".join([repr(type(a)), repr(a), repr(type(b)),
                        repr(b), "cannot be compared."])
        raise NotImplementedError(msg)

    return RV


def _approx_equal(a, b, tolerance):
    """Check if difference between two numbers is inside tolerance range."""
    if abs(a - b) <= tolerance * a:
        return True
    else:
        return False


def compare_list_values(values1, values2):
    """Check that all values of both lists are approximately equal.

    Args:
        values1: A list of values.
        values2: A lista of values.

    Returns:
        True (values1 elem are approximately equal than values2) or False.
    """

    RV = True

    for value1, value2 in zip(values1, values2):
        # print value1, value2, value2/value1-1
        if not approx_equal(value1, value2, 0.0001):
            RV = False
            break

    return RV
