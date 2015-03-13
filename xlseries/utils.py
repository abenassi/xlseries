import pandas as pd
from openpyxl import load_workbook


def approx_equal(a, b, tolerance):
    return abs(a - b) < tolerance * a


def infer_freq(av_seconds, tolerance=0.1):

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

    dfs = []

    wb = load_workbook(filename=xl_file, use_iterators=True)
    ws_names = wb.get_sheet_names()

    for ws_name in ws_names:
        df = get_data_frame(xl_file, sheetname=ws_name)
        dfs.append(df)

    return dfs


def get_data_frame(xl_file, sheetname=0):

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
