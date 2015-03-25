import os
import pandas as pd
import numpy as np
from openpyxl import load_workbook
from pandas.util.testing import assert_frame_equal
import json
import datetime


def load_file(rel_dir="./", fn_name_parser=str, file_format=".txt",
              load_obj=open, kw_arg="file_name"):
    """Call a function loading a file of the same name."""

    def fn_decorator(fn):
        relative_path = rel_dir + fn_name_parser(fn.__name__) + file_format
        file_loaded = load_obj(relative_path)

        def fn_decorated(*args, **kwargs):
            kwargs[kw_arg] = file_loaded
            fn(*args, **kwargs)

        fn_decorated.__name__ = fn.__name__
        return fn_decorated
    return fn_decorator


def load_json_vals(rel_dir="./", fn_name_parser=str, kw_arg="values",
                     json_file_name="values", evaluate=False):
    """Call a function loading values from json using fn name as a key."""

    def fn_decorator(fn):
        relative_path = rel_dir + json_file_name + ".json"
        with open(relative_path) as f:
            file_loaded = json.load(f)
        values = file_loaded[fn_name_parser(fn.__name__)]

        if evaluate:
            values = [eval(value) for value in values]

        def fn_decorated(*args, **kwargs):
            kwargs[kw_arg] = values
            fn(*args, **kwargs)

        fn_decorated.__name__ = fn.__name__
        return fn_decorated
    return fn_decorator


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
        os.chdir(os.path.join(package_dir, rel_working_dir))

        def test_decorated(*args, **kwargs):
            fn(*args, **kwargs)

        test_decorated.__name__ = fn.__name__
        return test_decorated
    return test_decorator


def compare_cells(wb1, wb2):
    """Compare two excels based on row iteration."""

    # compare each cell of each worksheet
    for ws1, ws2 in zip(wb1.worksheets, wb2.worksheets):
        for row1, row2 in zip(ws1.iter_rows(), ws2.iter_rows()):
            for cell1, cell2 in zip(row1, row2):

                msg = "".join([_safe_str(cell1.value), " != ",
                               _safe_str(cell2.value), "row: ", str(cell1.row),
                               "column: ", str(cell1.column)])

                try:
                    value1 = float(cell1.value)
                    value2 = float(cell2.value)
                except:
                    value1 = cell1.value
                    value2 = cell2.value

                if type(value1) == float and type(value2) == float:
                    assert approx_equal(cell1.value, cell2.value, 0.00001), msg
                else:
                    assert cell1.value == cell2.value, msg
    return True


def _safe_str(value):

    if not value:
        RV = str(value)

    elif type(value) == str or type(value) == unicode:
        RV = value.encode("utf-8")

    else:
        RV = str(value)

    return RV


def approx_equal(a, b, tolerance):
    """Check if a and b can be considered approximately equal."""

    RV = False

    if (not a) and (not b):
        RV = True

    elif np.isnan(a) and np.isnan(b):
        # print a, type(a), "not approx_equal to", b, type(b)
        RV = True

    elif a and (a != np.nan) and b and (b != np.nan):
        RV = _approx_equal(a, b, tolerance)

    else:
        RV = a == b

    return RV


def _approx_equal(a, b, tolerance):
    if abs(a - b) < tolerance * a:
        return True
    else:
        return False


def infer_freq(av_seconds, tolerance=0.1):
    """Infer frequency of a time data series."""

    if approx_equal(1, av_seconds, tolerance):
        freq = 'S'
    elif approx_equal(60, av_seconds, tolerance):
        freq = 'T'
    elif approx_equal(3600, av_seconds, tolerance):
        freq = 'H'
    elif approx_equal(86400, av_seconds, tolerance):
        freq = 'D'
    elif approx_equal(604800, av_seconds, tolerance):
        freq = 'W'
    elif approx_equal(2419200, av_seconds, tolerance):
        freq = 'M'
    elif approx_equal(7776000, av_seconds, tolerance):
        freq = 'Q'
    elif approx_equal(15552000, av_seconds, tolerance):
        raise Exception("Can't handle semesters!")
    elif approx_equal(31536000, av_seconds, tolerance):
        freq = 'Y'
    else:
        raise Exception("Average seconds don't match any frequency.")

    return freq


def get_data_frames(xl_file):
    """Parse a well formatted excel file into pandas data frames."""

    dfs = []

    wb = load_workbook(filename=xl_file, use_iterators=True)
    ws_names = wb.get_sheet_names()

    for ws_name in ws_names:
        df = get_data_frame(xl_file, sheetname=ws_name)
        dfs.append(df)

    return dfs


def get_data_frame(xl_file, sheetname=0):
    """Parse a well formatted excel sheet into a pandas data frame."""

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
    """

    try:
        assert df1.index.size == df2.index.size, "Different index size"
        assert df1.index.freqstr == df2.index.freqstr, "Different index freq"
        assert _check_columns(df1.columns, df2.columns), "Different columns"
        assert _check_index(df1.index, df2.index), "Different index"
        assert _check_values(df1.columns, df1, df2), "Too different values"

        return True

    except Exception as inst:
        print inst
        return False


def _check_columns(cols1, cols2):
    """Check both column lists are equal."""

    for col1 in cols1:
        if col1 not in cols2:
            return False

    for col2 in cols2:
        if col2 not in cols1:
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


def compare_list_values(values1, values2):
    """Check that all values of both lists are approximately equal."""

    RV = True

    for value1, value2 in zip(values1, values2):
        # print value1, value2, value2/value1-1
        if not approx_equal(value1, value2, 0.0001):
            print value1, type(value1), "not approx_equal to", value2, type(value2)
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
