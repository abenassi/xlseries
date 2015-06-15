#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
profiling

Profiling tool to analyze the time consumed by each part of the package.

Requirements:
    graphviz tool must be installed on your system 'brew install graphviz'
    pycallgraph==1.0.1 'pip install pycallgraph==1.0.1'

Example:
    # will run single and group analysis over all test cases
    python profiling

    import profiling
    profiling.main()

    # will run only single analysis over test cases 2, 3 and 4
    import profiling
    profiling.main(2, 4, False, True)

    # will run a single analysis over test case number 2
    import profiling
    profiling.single(2)

    # will run a group analysis over test cases 4 and 5, together
    import profiling
    profiling.group(4, 5)

The output is a png file, but it can be changed to a Gephi output than can be
analyzed with Gephi.
"""

from __future__ import unicode_literals
import os
# import yappi
from pycallgraph import PyCallGraph
from pycallgraph import Config
from pycallgraph import GlobbingFilter
from pycallgraph.output import GraphvizOutput
# from pycallgraph.output import GephiOutput


from xlseries import XlSeries
from xlseries.utils.path_finders import get_orig_cases_path
from xlseries.utils.path_finders import get_param_cases_path


REL_WORKING_DIR = r"tests\integration_cases"
PACKAGE_NAME = "xlseries"


def _run_test_case(num=1):
    """Run an integration test case.

    Args:
        num (int): Test case number.
    """
    xlseries = XlSeries(get_orig_cases_path(num))
    xlseries.get_data_frames(get_param_cases_path(num))


def _generate_name_output(ini, end=None, pre="profiling_case_", post=".png"):
    """Create the name of the file, like: "profiling_cases_1-2-3.png".

    Args:
        ini (int): First test case number analyzed.
        end (int): Last test case number analyzed.
        pre (str): Prefix to be added at the begining of the filename.
        post (str): Suffix to be appended at the end of the filename.

    Returns:
        str: The output filename.
    """
    if end:
        pre = "profiling_cases_"
        fname = pre + "-".join([str(i) for i in xrange(ini, end + 1)]) + post
    else:
        fname = pre + str(ini) + post

    return os.path.join("profiling_graphs", fname)


def single_analysis(ini, end=None, config=None):
    """Perform profiling analysis for each test case, separately.

    Args:
        ini (int): First test case number analyzed.
        end (int): Last test case number analyzed.
        config (Config): Configuration object for PyCallGraph.
    """

    for num in xrange(ini, end + 1):
        # graphviz = GephiOutput()
        graphviz = GraphvizOutput()
        graphviz.output_file = _generate_name_output(num)

        print "Running test case number", num, "in a single analysis."
        with PyCallGraph(output=graphviz, config=config):
            _run_test_case(num)


def group_analysis(ini, end, config=None):
    """Perform one profiling analysis for all the test cases, together.
    Args:
        ini (int): First test case number analyzed.
        end (int): Last test case number analyzed.
        config (Config): Configuration object for PyCallGraph.
    """

    # graphviz = GephiOutput()
    graphviz = GraphvizOutput()
    graphviz.output_file = _generate_name_output(ini, end)

    with PyCallGraph(output=graphviz, config=config):
        for num in xrange(ini, end + 1):
            print "Running test case number", num, "in a group analysis."
            _run_test_case(num)


def main(ini=1, end=5, group=True, single=True):

    config = Config()
    config.trace_filter = GlobbingFilter(exclude=[
        'a_module_you_want_to_exclude.*',
        '*.a_function_you_want_to_exclude',
    ])

    if single:
        single_analysis(ini, end)

    if group:
        group_analysis(ini, end)


if __name__ == '__main__':
    main(1, 4)
