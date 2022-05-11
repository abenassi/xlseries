#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Functions to deal with float precission issues

Allow to infer the significant figures of a float number to get read of
unnecessary decimals due to precission issues.
"""

import decimal
import math

import numpy as np




def significant_figures(serie):
    """ Calculates significant figures of a serie of numeric values

    Significant figures is the maximum number of decimals needed to preserve
    inferred numeric value precission of each value in the series. If a series
    has a 2 significant figures value and another with 3 significant figures,
    series will have 3 significant figures.
    """

    figures = 0
    serie = [x for x in serie if not np.isnan(x)]
    for value in serie:
        figure = infer_decimals(value)
        figures = max(figures, -figure)

    return figures




def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper




def infer_decimals(value):
    """ Calculates significant decimals of a value, correcting imprecission
​
    A value like 1.0000000000000001 (common when serializing floating
    nombers) gets truncated to 17 - N digits, being N the number of integer
    digits of the same indicator. Goal is cutting error margin given by float
    precission having 1.0000000000000001 ---> 1.0
    """
    integer_digits = len(str(int(math.modf(value)[1])))
    truncated = truncate(value, 17 - integer_digits)
    return decimal.Decimal(str(truncated)).normalize().as_tuple().exponent
