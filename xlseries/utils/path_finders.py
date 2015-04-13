#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
path_finders
----------------------------------

Auxiliar methods to quickly find a directory in the package.
"""

from __future__ import unicode_literals
import os


def get_param_cases_dir():
    """Return the path to integration test cases parameters."""

    relative_path = os.path.sep.join(["tests",
                                      "integration_cases",
                                      "parameters"])

    return os.path.join(get_package_dir("xlseries", __file__),
                        relative_path)


def get_orig_cases_dir():
    """Return the path to integration excel original test cases."""

    relative_path = os.path.sep.join(["tests",
                                      "integration_cases",
                                      "original"])

    return os.path.join(get_package_dir("xlseries", __file__),
                        relative_path)


def get_exp_cases_dir():
    """Return the path to integration excel expected test cases."""

    relative_path = os.path.sep.join(["tests",
                                      "integration_cases",
                                      "expected"])

    return os.path.join(get_package_dir("xlseries", __file__),
                        relative_path)


def get_package_dir(package_name, inside_path):
    """Get the directory of a package given an inside path.

    Recursively get parent directories until package_name is reached.

    Args:
        package_name: Name of the package to retrieve directory.
        inside_path: A path inside the package.
    """

    if os.path.split(inside_path)[1] == package_name and \
            os.path.basename(os.path.split(inside_path)[0]) != package_name:
        return inside_path

    else:
        return get_package_dir(package_name, os.path.split(inside_path)[0])
