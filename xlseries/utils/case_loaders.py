#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
case_loaders
----------------------------------

Auxiliar methods to quickly load an integration case file.
"""

from __future__ import unicode_literals
import os
from openpyxl import load_workbook

from xlseries.strategies.discover.parameters import Parameters
from xlseries.utils.data_frame import get_data_frames
from xlseries.utils.path_finders import get_orig_cases_dir
from xlseries.utils.path_finders import get_param_cases_dir
from xlseries.utils.path_finders import get_exp_cases_dir


def load_original_case(case_num=1, **loader_args):
    """Load an original integration test case file.

    Args:
        case_num: Number of the case to load.
        loader_args: Aditional key word arguments to load the excel file.

    Returns:
        A Workbook with original test case excel file loaded in it.
    """

    case_name = "test_case" + unicode(case_num) + ".xlsx"
    # raise Exception(get_orig_cases_dir())
    case_path = os.path.join(get_orig_cases_dir(), case_name)

    # look at data rather than formulae
    loader_args["data_only"] = True

    return load_workbook(case_path, **loader_args)


def load_parameters_case(case_num=1):
    """Load the parameters of an integration test case.

    Args:
        case_num: Number of the case to load.

    Returns:
        A Parameters object with test case parameters loaded.
    """

    case_name = "test_case" + unicode(case_num) + ".json"
    case_path = os.path.join(get_param_cases_dir(), case_name)

    return Parameters(case_path)


def load_expected_case(case_num=1):
    """Load an original integration case file.

    Args:
        case_num: Number of the case to load.

    Returns:
        A Workbook with original test case excel file loaded in it.
    """

    case_name = "test_case" + unicode(case_num) + ".xlsx"
    case_path = os.path.join(get_exp_cases_dir(), case_name)

    return get_data_frames(case_path)
