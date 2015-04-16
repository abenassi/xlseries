#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
path_finders
----------------------------------

Auxiliar methods to quickly find a directory in the package.
"""

from __future__ import unicode_literals
import os
import sys
import inspect


class PackageDirNotFound(Exception):
    pass


def abs_path(relative_path, parent_level=1):
    """Generate absolute path based on file's directory.

    Args:
        relative_path: Relative path from the directory of the file in which a
            function is called.

    Returns:
        An absolute path joining the relative path and the files directory.
    """

    parent_frame = inspect.stack()[parent_level][0]
    parent_module = inspect.getmodule(parent_frame)
    parent_dir = os.path.dirname(parent_module.__file__)

    return os.path.join(parent_dir, relative_path)


def get_param_cases_dir():
    return get_param_cases_path()


def get_param_cases_path(case_num=None):
    """Return the path to integration test cases parameters."""

    relative_path = os.path.sep.join(["tests",
                                      "integration_cases",
                                      "parameters"])

    base_dir = os.path.join(get_package_dir("xlseries", __file__),
                            relative_path)

    if not case_num:
        return base_dir

    # if a case number is provided, return full path to the file
    else:
        file_name = "test_case" + unicode(case_num) + ".json"
        return os.path.join(base_dir, file_name)


def get_orig_cases_dir():
    return get_orig_cases_path()


def get_orig_cases_path(case_num=None):
    """Return the path to integration excel original test cases."""

    relative_path = os.path.sep.join(["tests",
                                      "integration_cases",
                                      "original"])

    base_dir = os.path.join(get_package_dir("xlseries", __file__),
                            relative_path)

    if not case_num:
        return base_dir

    # if a case number is provided, return full path to the file
    else:
        file_name = "test_case" + unicode(case_num) + ".xlsx"
        return os.path.join(base_dir, file_name)


def get_exp_cases_dir():
    return get_exp_cases_path()


def get_exp_cases_path(case_num=None):
    """Return the path to integration excel expected test cases."""

    relative_path = os.path.sep.join(["tests",
                                      "integration_cases",
                                      "expected"])

    base_dir = os.path.join(get_package_dir("xlseries", __file__),
                            relative_path)

    if not case_num:
        return base_dir

    # if a case number is provided, return full path to the file
    else:
        file_name = "test_case" + unicode(case_num) + ".xlsx"
        return os.path.join(base_dir, file_name)


def get_screenshot_cases_dir():
    return get_exp_cases_path()


def get_screenshot_cases_path(case_num=None):
    """Return the path to integration excel screenshots of test cases."""

    relative_path = os.path.sep.join(["docs",
                                      "xl_screenshots"])

    base_dir = os.path.join(get_package_dir("xlseries", __file__),
                            relative_path)

    if not case_num:
        return base_dir

    # if a case number is provided, return full path to the file
    else:
        file_name = "test_case" + unicode(case_num) + ".png"
        return os.path.join(base_dir, file_name)


def get_package_dir(package_name, inside_path):
    """Get the directory of a package given an inside path.

    Recursively get parent directories until package_name is reached.

    Args:
        package_name: Name of the package to retrieve directory.
        inside_path: A path inside the package.
    """

    # go up in the tree folder looking for the root directory of the package
    if os.path.isabs(inside_path):
        if os.path.split(inside_path)[1] == package_name and \
                os.path.basename(os.path.split(inside_path)[0]) != package_name:
            return inside_path

        else:
            return get_package_dir(package_name, os.path.split(inside_path)[0])

    # look at the enviormental variables for the package path
    else:
        for path in sys.path:
            if os.path.basename(path) == package_name:
                return path

        raise PackageDirNotFound(package_name + " dir couldn't be found.")
