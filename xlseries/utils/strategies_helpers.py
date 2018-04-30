#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
strategies_helpers

This module contains auxiliary methods to retrieve the strategies available
in any module where these methods are called. The following filters apply to
pass only useful strategies from a strategy module and avoid passing auxiliary
classes or abstract base strategies that are not designed with the user
interface expected by the user of the strategies:
    - Class names starting with "Base" are not passed
    - Subclasses of Exception are not passed
    - Parameters class is not passed
"""

import inspect


def get_strategies_names(parent_level=2):
    """Returns a list of the strategy names in parent module.

    Avoids to return base classes, Parameters class and exception classes."""

    parent_classes = get_parent_module_classes(parent_level)

    cls_names = [cls_name for cls_name in parent_classes if
                 cls_name[:4] != "Base" and
                 cls_name != "Parameters" and
                 not issubclass(parent_classes[cls_name], Exception)]

    return cls_names


def get_strategies(parent_level=2):
    """Returns a list of references to strategy classes in parent module.

    Args:
        parent_level: Number of levels to go up looking for a parent module.

    Returns:
        [parent_class1, parent_class2, parent_class3...] Only the classes
        filtered by get_strategies_names are passeed.
    """

    parent_classes = get_parent_module_classes(parent_level)
    return [parent_classes[cls_name] for cls_name in
            get_strategies_names(parent_level + 1)]


def get_parent_module_classes(parent_level):
    """Generates a dictionary of classes in parent module namespace.

    Inspect the strack getting a reference to the module in which this
    function was called. Build a dictionary with references to all the classes
    in the namespace of that module.

    Args:
        parent_level: Number of levels to go up looking for the parent.

    Returns:
        {"class_name": class_reference}
    """

    parent_frame = inspect.stack()[parent_level][0]
    parent_module = inspect.getmodule(parent_frame)

    return {cls_tupl[0]: cls_tupl[1] for cls_tupl in
            inspect.getmembers(parent_module, inspect.isclass)}
