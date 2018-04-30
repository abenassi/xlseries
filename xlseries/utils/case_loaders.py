#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
case_loaders

Auxiliar methods to quickly load an integration case file.
"""

import os
from openpyxl import load_workbook

from xlseries.strategies.discover.parameters import Parameters
from .data_frame import get_data_frames, compare_data_frames
from .path_finders import get_orig_cases_dir
from .path_finders import get_param_cases_dir
from .path_finders import get_exp_cases_dir


def check_case_exp_result(case_num, dfs):
    """Check that a list of dfs is the expected result of a test case.

    Run a compare_data_frames check between each pair of data frames. If there
    is a difference, and AssertionError will be raised. Prints OK if no
    difference is found.

    Args:
        case_num (int): Number of test case.
        dfs (list): List of DataFrame objects.
    """
    for df, exp_df in zip(dfs, load_expected_case(case_num)):
        compare_data_frames(df, exp_df)

    print("OK")


def load_original_case(case_num=1, special_case=None, **loader_args):
    """Load an original integration test case file.

    Args:
        case_num (int): Number of the case to load.
        special_case (str): Name of a special version of the test case, if any.
        loader_args: Aditional key word arguments to load the excel file.

    Returns:
        Workbook: Original test case excel file loaded in it.
    """
    case_name = _gen_filename(case_num, special_case, "xlsx")
    case_path = os.path.join(get_orig_cases_dir(), case_name)

    # look at data rather than formulae
    loader_args["data_only"] = True

    return load_workbook(case_path, **loader_args)


def load_parameters_case(case_num=1, special_case=None):
    """Load the parameters of an integration test case.

    Args:
        case_num (int): Number of the case to load.
        special_case (str): Name of a special version of the test case, if any.

    Returns:
        Parameters: Test case parameters loaded.
    """
    case_name = _gen_filename(case_num, special_case, "json")
    case_path = os.path.join(get_param_cases_dir(), case_name)

    return Parameters(case_path)


def load_critical_parameters_case(case_num=1, special_case=None):
    """Load the critical parameters of an integration test case.

    Args:
        case_num (int): Number of the case to load.
        special_case (str): Name of a special version of the test case, if any.

    Returns:
        Parameters: object with test case critical parameters loaded.
    """
    params = load_parameters_case(case_num, special_case)
    params.remove_non_critical()

    return params


def load_expected_case(case_num=1, special_case=None):
    """Load an original integration case file.

    Args:
        case_num (int): Number of the case to load.
        special_case (str): Name of a special version of the test case, if any.

    Returns:
        Workbook: Original test case excel file loaded in it.
    """
    case_name = _gen_filename(case_num, special_case, "xlsx")
    case_path = os.path.join(get_exp_cases_dir(), case_name)

    return get_data_frames(case_path)


def _gen_filename(case_num=1, special_case="", file_format="xlsx"):
    special_case = special_case or ""
    return "test_case{}{}.{}".format(case_num, special_case, file_format)
