from pandas.util.testing import assert_frame_equal
from xlseries.utils import approx_equal


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
