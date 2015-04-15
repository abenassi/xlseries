#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
decorators
----------------------------------

Auxiliar decorators. They are probably not being used because they were
replace in tests by simpler helper methods. They remain in this module as
deprecated methods.
"""

from __future__ import unicode_literals
import json
from functools import wraps
import os

from xlseries.utils.path_finders import get_package_dir


def load_file(rel_dir=os.path.dirname(__file__),
              fn_name_parser=str, file_format=".txt",
              load_obj=open, kw_arg="file_name", loader_args={}):
    """Call a function loading a file of the same name."""

    def fn_decorator(fn):
        relative_path = rel_dir + fn_name_parser(fn) + file_format
        file_loaded = load_obj(relative_path, **loader_args)

        @wraps(fn)
        def fn_decorated(*args, **kwargs):
            kwargs[kw_arg] = file_loaded
            fn(*args, **kwargs)

        return fn_decorated
    return fn_decorator


def load_json_vals(rel_dir=os.path.dirname(__file__),
                   fn_name_parser=str, kw_arg="values",
                   json_file_name="values", evaluate=False):
    """Call a function loading values from json using fn name as a key."""

    def fn_decorator(fn):
        relative_path = rel_dir + json_file_name + ".json"
        # raise Exception(os.getcwd())
        with open(relative_path) as f:
            file_loaded = json.load(f)
        values = file_loaded[fn_name_parser(fn.__name__)]

        if evaluate:
            values = [eval(value) for value in values]

        @wraps(fn)
        def fn_decorated(*args, **kwargs):
            # kwargs[kw_arg] = values
            fn(*args, **kwargs)

        return fn_decorated
    return fn_decorator


def change_working_dir(package_name, rel_working_dir):
    """Decorate a function setting a new working directory.

    Working directory will be an absolute path inside the current package to
    match the relative working directory provided.

    Args:
        package_name: Name of the package that will provide root for all the
            absolute paths.
        rel_working_dir: Relative path the one containing package_name.
    """

    def test_decorator(fn):
        package_dir = get_package_dir(package_name, __file__)
        old_dir = os.getcwd()
        os.chdir(os.path.join(package_dir, rel_working_dir))

        @wraps(fn)
        def test_decorated(*args, **kwargs):
            fn(*args, **kwargs)
            os.chdir(old_dir)

        test_decorated.__name__ = fn.__name__
        return test_decorated
    return test_decorator
