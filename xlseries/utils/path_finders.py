#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
path_finders
----------------------------------

Auxiliar methods to quickly find a directory in the package.
"""

from __future__ import unicode_literals
import os
from xlseries.utils.general import get_package_dir


def get_tests_params_dir():
    """Return the path to integration test cases parameters."""

    relative_path = os.path.sep.join(["tests",
                                      "integration_cases",
                                      "parameters"])

    return os.path.join(get_package_dir("xlseries", __file__),
                        relative_path)


def get_xl_cases_dir():
    """Return the path to integration excel original test cases."""

    relative_path = os.path.sep.join(["tests",
                                      "integration_cases",
                                      "original"])

    return os.path.join(get_package_dir("xlseries", __file__),
                        relative_path)


def get_xl_exp_cases_dir():
    """Return the path to integration excel expected test cases."""

    relative_path = os.path.sep.join(["tests",
                                      "integration_cases",
                                      "expected"])

    return os.path.join(get_package_dir("xlseries", __file__),
                        relative_path)
