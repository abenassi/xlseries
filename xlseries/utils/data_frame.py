#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
data_frame
----------------------------------

Auxiliar methods to load and manipulate data frames.
"""

from __future__ import unicode_literals
import pandas as pd
from openpyxl import load_workbook
from time_manipulation import infer_freq
from xlseries.utils.general import approx_equal


def get_data_frames(xl_file):
    """Parse a well formatted excel file into pandas data frames.

    Args:
        xl_file: Path to an excel file with data ready to load into pandas
            data frame format.

    Returns:
        A list of pandas data frames.
    """

    dfs = []

    wb = load_workbook(filename=xl_file, use_iterators=True)
    ws_names = wb.get_sheet_names()

    for ws_name in ws_names:
        df = get_data_frame(xl_file, sheetname=ws_name)
        dfs.append(df)

    return dfs


def get_data_frame(xl_file, sheetname=0):
    """Parse a well formatted excel sheet into a pandas data frame.

    Args:
        xl_file: Path to an excel file with data ready to load into pandas
            data frame format.
        sheetname: Name or index of the excel sheet to be loaded.

    Returns:
        A pandas data frame."""

    df = pd.read_excel(xl_file, sheetname)

    # adopt a datetime index (first excel col)
    df = df.set_index(df.columns[0])

    time_delta = (df.index[-1] - df.index[0]) / df.index.size
    av_seconds = time_delta.total_seconds()
    period_range = pd.period_range(df.index[0],
                                   df.index[-1],
                                   freq=infer_freq(av_seconds))

    # rebuild data frame using a period range with frequency
    df = pd.DataFrame(data=df.values,
                      index=period_range,
                      columns=df.columns)

    return df


def compare_data_frames(df1, df2):
    """Compare two data frames.

    Args:
        df1: First data frame to compare.
        df2: Second data frame to compare.

    Returns:
        True (everything is the same in df1 and df2) or False.
    """

    msg = "Different index size"
    assert df1.index.size == df2.index.size, msg

    msg = "Different index freq"
    assert df1.index.freqstr == df2.index.freqstr, msg

    msg = "Different columns"
    assert _check_columns(df1.columns, df2.columns), msg

    msg = "Different index"
    assert _check_index(df1.index, df2.index), msg

    msg = "Too different values"
    assert _check_values(df1.columns, df1, df2), msg

    return True


def _check_columns(cols1, cols2):
    """Check both column lists are equal."""

    for col1 in cols1:
        if col1 not in cols2:
            msg = "".join(["'", col1, "'", "\nnot in\n",
                           "\n".join(list(cols2))])
            raise Exception(msg)

    for col2 in cols2:
        if col2 not in cols1:
            # raise Exception(repr(col2) + " not in " + repr(cols1))
            return False

    return True


def _check_index(index1, index2):
    """Check two time indexes are equal."""

    for date1, date2 in zip(index1, index2):
        if not date1 == date2:
            return False

    return True


def _check_values(cols, df1, df2):
    """Check that all values of both data frames are approximately equal."""

    RV = True

    for col in cols:
        for value1, value2 in zip(df1[col], df2[col]):
            # print value1, value2, value2/value1-1
            if not approx_equal(value1, value2, 0.0001):
                print "not approx_equal"
                RV = False
                break

    return RV


def compare_period_ranges(pr1, pr2):
    """Compare two period ranges.

    Args:
        pr1: First period range to compare.
        pr2: Second period range to compare.
    """

    try:
        assert pr1.freq == pr2.freq, "Different frequency"
        assert pr1[0] == pr2[0], "Different initial date"
        assert pr1[-1] == pr2[-1], "Different final date"

        return True

    except Exception as inst:
        print inst
        return False


def compare_data_frames_pandas(df1, df2):
    """Wrapper to compare two data frames using assert_frame_equal.

    Args:
        df1: First data frame to compare.
        df2: Second data frame to compare.
    """

    try:
        # returns None when data frames are equal
        assert_frame_equal(df1, df2,
                           check_dtype=True,
                           check_index_type=True,
                           check_column_type=True,
                           check_frame_type=True,
                           check_less_precise=True,
                           check_names=True,
                           by_blocks=True,
                           check_exact=True)
        return True

    except Exception as inst:
        print inst
        return False
