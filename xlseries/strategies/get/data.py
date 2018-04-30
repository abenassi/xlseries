#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
data

This module contains strategies to get data from a spreadsheet.

Warning! Do not import other classes directly "from module import Class",
except if they are custom exceptions.
Rather import the module in which the Class is defined and use it like
"module.Class". All the classes defined in this modul namespace are
automatically taken by "get_strategies" and exposed to the user.
"""

from pprint import pprint
import arrow
import datetime
import numpy as np
from unidecode import unidecode
import collections

import xlseries.utils.strategies_helpers
from xlseries.utils.time_manipulation import increment_time


class BaseGetDataStrategy(object):

    """Implements the interface for all get data strategies."""

    # PUBLIC INTERFACE
    @classmethod
    def accepts(cls, ws, params):
        return cls._accepts(ws, params)

    def get_data(self, ws, params):
        return self._get_data(ws, params)

    # PRIVATE
    @classmethod
    def _accepts(cls, ws, params):
        """Accepts inputs that are accepted by all the base classes."""
        return cls._base_cond(ws, params)

    def _get_data(self, ws, params):
        name = self._get_name(ws, params["headers_coord"],
                              params["composed_headers_coord"],
                              params["context"],
                              params["series_names"])
        # print name
        values_list = self._get_values(ws, params)
        # print params["data_ends"]

        return [(name, values) for values in values_list]

    @classmethod
    def _get_name(cls, ws, header_coord, composed_headers_coord=None,
                  context=None, series_names=None):
        """Get the header name of a series.

        Args:
            ws (worksheet): A worksheet with time series.
            header_coord (str): Coordinate of the header.
            composed_headers_coord (list): Coordinates of the composed headers
                that add information previous to the header.
            context (list): Strings that provide the context of the header,
                adding also more information in a higher level (categories).
            series_names (str): An alternative name for the series.

        Returns:
            str: Complete name of a series.
        """

        if series_names:
            name = series_names

        else:
            name = unidecode(str(ws[header_coord].value)).strip()

            if composed_headers_coord:
                msg = " ".join(["Composed is not list",
                                repr(type(composed_headers_coord)),
                                repr(composed_headers_coord)])
                assert isinstance(composed_headers_coord, list), msg

                name = " ".join([unidecode(ws[coord].value).strip() for
                                 coord in composed_headers_coord] + [name])

            if context:
                msg = " ".join(["Context is not list", repr(type(context)),
                                repr(context)])
                assert isinstance(context, list), msg

                name = " - ".join([header_context.strip() for
                                   header_context in context] + [name])

        return name

    def _get_values(self, ws, params):
        p = params
        # create iterator of values
        iter_values = self._values_iterator(ws, p["alignment"],
                                            p["headers_coord"],
                                            p["data_starts"],
                                            p["data_ends"])

        values_dict = collections.OrderedDict()
        for value, index in iter_values:
            new_value = self._handle_new_value(list(values_dict.values()), value,
                                               p["missings"],
                                               p["missing_value"],
                                               p["blank_rows"])

            if self._value_to_be_added(new_value, index, ws, p):
                frequency = self._get_frequency(p["frequency"])
                if frequency not in values_dict:
                    values_dict[frequency] = []
                values_dict[frequency].append(new_value)

        # fill the missing values if they are implicit
        # it doesn't work with multifrequency series
        if (p["missings"] and "Implicit" in p["missing_value"] and
                len(p["frequency"]) == 1):
            values = list(values_dict.values())[0]
            values = self._fill_implicit_missings(ws,
                                                  values,
                                                  p["frequency"],
                                                  p["time_header_coord"],
                                                  p["data_starts"],
                                                  p["data_ends"],
                                                  p["alignment"])
            return [values]

        return list(values_dict.values())

    @classmethod
    def _values_iterator(cls, ws, alignment, header_coord, ini, end):

        if alignment == "vertical":
            col = ws[header_coord].column
            for row in range(ini, end + 1):
                yield (ws[col + str(row)].value, row)

        elif alignment == "horizontal":
            row = ws[header_coord].row
            for col in range(ini, end + 1):
                yield (ws.cell(column=col, row=row).value, col)

        else:
            raise Exception("Series alignment must be 'vertical' or " +
                            "'horizontal', not " + repr(alignment))

    @classmethod
    def _time_index_iterator(cls, ws, alignment, time_header_coord, ini, end):

        if alignment == "vertical":
            for row in range(ini, end + 1):
                col = cls._time_header_cell(ws, time_header_coord).column
                yield ws[col + str(row)].value

        elif alignment == "horizontal":
            for col in range(ini, end + 1):
                row = cls._time_header_cell(ws, time_header_coord).row
                yield ws.cell(column=col, row=row).value

        else:
            raise Exception("Series alignment must be 'vertical' or " +
                            "'horizontal', not " + repr(alignment))

    @classmethod
    def _time_header_cell(cls, ws, time_header_coord):
        """Returns the column where clean time index shouls be written."""
        if isinstance(time_header_coord, list):
            return ws[time_header_coord[0]]
        else:
            return ws[time_header_coord]

    @classmethod
    def _valid_value(cls, value):
        """Check if a value is likely to be a series data value."""

        RV = True

        try:
            float(value)
        except:
            RV = False

        return RV


class BaseAccepts():

    """Provide the basic accepts conditions resolution."""

    @classmethod
    def _accepts(cls, ws, params):
        return cls._base_cond(ws, params)

    @classmethod
    def _base_cond(cls, ws, params):
        """Check that all base classes accept the input."""
        for base in cls.__bases__:
            if (
                base is not BaseGetDataStrategy and
                (hasattr(base, "_accepts") and not base._accepts(ws, params))
            ):
                return False
        return True


class BaseSingleFrequency():

    @classmethod
    def _accepts(cls, ws, params):
        return len(params["frequency"]) == 1

    # PRIVATE
    @classmethod
    def _fill_implicit_missings(cls, ws, values, frequency, time_header_coord,
                                ini, end, alignment):
        """Fill time holes in the series with missing data."""

        iter_ti = cls._time_index_iterator(ws, alignment, time_header_coord,
                                           ini, end)

        new_values = []
        exp_time = None
        for obs_time, (i_value, value) in zip(iter_ti, enumerate(values)):
            obs_time = arrow.get(obs_time)
            exp_time = exp_time or obs_time

            # fill time holes in the series with missing data
            while exp_time < obs_time:
                new_values.append(np.nan)
                exp_time = increment_time(exp_time, 1, frequency)

            new_values.append(values[i_value])
            exp_time = increment_time(exp_time, 1, frequency)

        return new_values

    @classmethod
    def _get_frequency(cls, frequency):
        return frequency


class BaseMultiFrequency():

    def __init__(self):
        self.last_frequency = None

    @classmethod
    def _accepts(cls, ws, params):
        return len(params["frequency"]) > 1

    def _get_frequency(self, frequency):
        freq, self.last_frequency = self._next_frequency(frequency,
                                                         self.last_frequency)
        return freq

    @classmethod
    def _next_frequency(cls, frequency, last_frequency=None):
        """Calculates what frequency go next.

        In single frequency series, returns the frequency parameter. This
        method gains relevance in multifrequency series, where a tracking of
        the last frequency is needed to know what frequency should be applied
        for a time value in a certain point of the time index.
        """

        if not len(frequency) > 1:
            return frequency

        if not last_frequency or last_frequency == frequency:
            freq = frequency[0]
            last_frequency = freq
        else:
            # print frequency.partition(last_frequency)
            freq = frequency.partition(last_frequency)[2][0]
            assert len(freq) == 1, "Freq must have only one character."
            last_frequency += freq

        # print freq, last_frequency

        return freq, last_frequency


class BaseContinuous():

    """Get data from continuous series."""

    @classmethod
    def _accepts(cls, ws, params):
        return params["continuity"]

    @classmethod
    def _value_to_be_added(cls, value, index, ws, params):
        """Check if a value should be added or not."""
        return value is not None

    @classmethod
    def _handle_new_value(cls, values, value, missings, missing_value,
                          blank_rows):

        if blank_rows and value is None:
            return None

        if missings:
            if isinstance(value, str) or isinstance(value, str):
                value = value.strip()

            if value not in missing_value:
                args_without_values = locals()
                del args_without_values["values"]
                try:
                    return float(value)
                except:
                    # print args_without_values
                    raise Exception("Value is not valid " + str(value))
            else:
                return np.nan
        else:
            return float(value)


class BaseNonContinuous():

    """Get data from non continuous series."""

    @classmethod
    def _accepts(cls, ws, params):
        return not params["continuity"]

    @classmethod
    def _value_to_be_added(cls, value, index, ws, params):
        """Check if a value should be added or not.

        Value shouldn't be None and the row should correspond to a valid time
        value in the time index."""

        # keep the first column in case time index is multicolumn
        if params["time_multicolumn"]:
            time_header_coord = params["time_header_coord"][0]
        else:
            time_header_coord = params["time_header_coord"]

        if params["alignment"] == "vertical":
            time_col = ws[time_header_coord].column
            time_coord = time_col + str(index + params["time_alignment"])
            time_value = ws[time_coord].value

        elif params["alignment"] == "horizontal":
            time_row = ws[time_header_coord].row
            time_value = ws.cell(column=index + params["time_alignment"],
                                 row=time_row).value

        else:
            raise Exception("Series alignment must be 'vertical' or " +
                            "'horizontal', not " + repr(params["alignment"]))

        return value is not None and isinstance(time_value, datetime.datetime)

    @classmethod
    def _handle_new_value(cls, values, value, missings, missing_value,
                          blank_rows):
        if ((isinstance(value, str) or isinstance(value, str)) and
                value.strip() == ""):
            value = None

        new_value = None
        if missings:
            if value in missing_value:
                new_value = np.nan
            elif cls._valid_value(value):
                new_value = float(value)
            # values that are not valid nor missings
            else:
                pass
        else:
            if cls._valid_value(value):
                new_value = float(value)

        return new_value


def get_strategies():
    custom = xlseries.utils.strategies_helpers.get_strategies()

    combinations = []
    for freq in [BaseSingleFrequency, BaseMultiFrequency]:
        for cont in [BaseContinuous, BaseNonContinuous]:

            name = freq.__name__ + cont.__name__
            bases = (BaseAccepts, freq, cont, BaseGetDataStrategy)
            parser = type(name, bases, {})

            combinations.append(parser)

    return custom + combinations

if __name__ == '__main__':
    pprint(sorted(xlseries.utils.strategies_helpers.get_strategies_names()))
