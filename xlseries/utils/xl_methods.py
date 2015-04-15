#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
xl_methods
----------------------------------

Useful methods for excel operations and related manipulations.
"""

from openpyxl import Workbook
from xlseries.utils.general import approx_equal


def xl_coordinates_range(start, end=None):
    """Creates a generator of excel coordinates.

    Args:
        start: Excel coordinate where range starts (eg. "A5").
        end: Excel coordinate where range ends (eg. "C7").

    Yields:
        A string with the coordinate that follows the previous one
            in a range. This are yielded row by row.

    >>> for coord in xl_coordinates_range("A1", "B2"):
    ...     print coord
    'A1'
    'A2'
    'B1'
    'B2'
    """

    ws = Workbook().active

    if end:
        for row in ws[start + ":" + end]:
            for cell in row:
                yield cell.coordinate
    else:
        yield start


def compare_cells(wb1, wb2):
    """Compare two excels based on row iteration."""

    # compare each cell of each worksheet
    for ws1, ws2 in zip(wb1.worksheets, wb2.worksheets):
        for row1, row2 in zip(ws1.rows, ws2.rows):
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


if __name__ == '__main__':
    import doctest
    doctest.testmod()
