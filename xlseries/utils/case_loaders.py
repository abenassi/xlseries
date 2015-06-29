#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
case_loaders

Auxiliar methods to quickly load an integration case file.
"""

from __future__ import unicode_literals
import os
from openpyxl import load_workbook

from xlseries.strategies.discover.parameters import Parameters
from data_frame import get_data_frames, compare_data_frames
from path_finders import get_orig_cases_dir
from path_finders import get_param_cases_dir
from path_finders import get_exp_cases_dir


def check_case_exp_result(case_num, dfs):
    exp_dfs = load_expected_case(case_num)
    for df, exp_df in zip(dfs, exp_dfs):
        msg = "Different result."
        assert compare_data_frames(df, exp_df), msg
    print "OK"


def load_original_case(case_num=1, special_version=None, **loader_args):
    """Load an original integration test case file.

    Args:
        case_num: Number of the case to load.
        loader_args: Aditional key word arguments to load the excel file.

    Returns:
        A Workbook with original test case excel file loaded in it.
    """

    if special_version:
        case_name = "test_case" + unicode(case_num) + unicode(special_version) + ".xlsx"
    else:
        case_name = "test_case" + unicode(case_num) + ".xlsx"
    # raise Exception(get_orig_cases_dir())
    case_path = os.path.join(get_orig_cases_dir(), case_name)

    # look at data rather than formulae
    loader_args["data_only"] = True

    return load_workbook(case_path, **loader_args)


def load_parameters_case(case_num=1, special_version=None):
    """Load the parameters of an integration test case.

    Args:
        case_num: Number of the case to load.

    Returns:
        A Parameters object with test case parameters loaded.
    """

    if special_version:
        case_name = "test_case" + unicode(case_num) + unicode(special_version) + ".json"
    else:
        case_name = "test_case" + unicode(case_num) + ".json"
    case_path = os.path.join(get_param_cases_dir(), case_name)

    return Parameters(case_path)


def load_critical_parameters_case(case_num=1, special_version=None):
    """Load the critical parameters of an integration test case.

    Args:
        case_num (int): Number of the case to load.

    Returns:
        Parameters: object with test case critical parameters loaded.
    """

    if special_version:
        case_name = "test_case" + unicode(case_num) + unicode(special_version) + ".json"
    else:
        case_name = "test_case" + unicode(case_num) + ".json"
    case_path = os.path.join(get_param_cases_dir(), case_name)
    params = Parameters(case_path)
    params.remove_non_critical()

    return params


def load_expected_case(case_num=1, special_version=None):
    """Load an original integration case file.

    Args:
        case_num: Number of the case to load.

    Returns:
        A Workbook with original test case excel file loaded in it.
    """

    if special_version:
        case_name = "test_case" + unicode(case_num) + unicode(special_version) + ".xlsx"
    else:
        case_name = "test_case" + unicode(case_num) + ".xlsx"
    case_path = os.path.join(get_exp_cases_dir(), case_name)

    return get_data_frames(case_path)
