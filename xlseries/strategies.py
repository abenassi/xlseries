#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
strategies
----------------------------------

This module contains the hight level strategies used by `xlseries` to parse
time data series inside excel files into Pandas DataFrames.
"""

import copy
import os
from pprint import pprint
import pyclbr
import pandas as pd
import numpy as np
import datetime
import json
from parameters import Parameters
from utils import get_data_frames
from openpyxl.cell import coordinate_from_string, column_index_from_string


class BaseStrategy(object):

    """BaseStrategy class for all strategies."""

    def __init__(self, wb, input_params=Parameters()):
        self.wb = wb
        self.params = input_params

    # PUBLIC INTERFACE
    @classmethod
    def accepts(cls, wb):
        return cls._accepts(wb)

    def get_data_frames(self):
        return self._get_data_frames()


class ParameterDiscovery(BaseStrategy):

    """Strategy that aims to discover key parsing parameters."""

    MAX_IMPL = 7

    # PRIVATE INTERFACE METHODS
    @classmethod
    def _accepts(cls, wb):
        return True

    def _get_data_frames(self):
        """Extract time data series and return them as data frames."""

        ws = self.wb.active

        # First: discover the parameters of the file
        self._discover_parameters(ws)

        # Second: clean the data
        self._clean_data(ws)

        # Third: get the data
        return self._get_data(ws)

    # HIGH LEVEL TASKS
    def _discover_parameters(self, ws):
        """Discover the parameters of the worksheet."""
        pass

    def _clean_data(self, ws):
        """Ensure data is clean to be processed with the parameters."""

        for (time_alignment, time_format, time_header_coord,
             ini_row, end_row, freq, miss_presence, missing_value) in \
            zip(self.params.time_alignment,
                self.params.time_format,
                self.params.time_header_coord,
                self.params.data_starts,
                self.params.data_ends,
                self.params.frequency,
                self.params.missings,
                self.params.missing_value):

            status_index = self._clean_time_index(ws, time_alignment,
                                                  time_format,
                                                  time_header_coord,
                                                  ini_row, end_row,
                                                  freq, miss_presence,
                                                  missing_value)

            status_values = self._clean_values(ws)

        return {"index": status_index, "values": status_values}

    def _get_data(self, ws):
        """Parse data using parameters and return it in data frames."""

        # build period ranges
        period_ranges = self._get_period_ranges(ws)

        # build frames dict based on amount of frequencies
        frames_input_dict = {}
        for freq in self.params.frequency:
            frames_input_dict[freq] = {"columns": [], "data": []}

        # get name and data of each data series
        for header_coord, freq, ini_row, end_row in \
            zip(self.params.headers_coord, self.params.frequency,
                self.params.data_starts, self.params.data_ends):

            columns = frames_input_dict[freq]["columns"]
            data = frames_input_dict[freq]["data"]

            name = self._get_name(ws, header_coord)
            columns.append(name)

            values = self._get_values(ws, header_coord, ini_row, end_row)
            data.append(values)

        # build data frames
        dfs = []
        for period_range in period_ranges:
            columns = frames_input_dict[period_range.freqstr]["columns"]
            data = frames_input_dict[period_range.freqstr]["data"]
            np_data = np.array(data).transpose()

            df = pd.DataFrame(index=period_range,
                              columns=columns,
                              data=np_data)

            dfs.append(df)

        return dfs

    # 2. CLEAN DATA methods
    @classmethod
    def _clean_time_index(cls, ws, time_alignment, time_format,
                          time_header_coord, ini_row, end_row,
                          freq, miss_presence, missing_value):
        status_index = True

        col = column_index_from_string(ws[time_header_coord].column)

        # iterate series time index values
        i_row = ini_row
        last_time_value = None
        while i_row <= end_row:
            curr_time_value = ws.cell(row=i_row, column=col).value

            # clean curr time value, in case of format errors or no time values
            curr_time_value = cls._parse_time(curr_time_value, time_format)

            if curr_time_value:

                # correct date typos checking a healthy time progression
                new_time_value = None
                if curr_time_value and last_time_value:
                    new_time_value = cls._correct_progression(last_time_value,
                                                              curr_time_value,
                                                              freq,
                                                              miss_presence,
                                                              missing_value)
                    # if i_row == 2323:
                    #     print time_header_coord, freq, last_time_value, curr_time_value, new_time_value, i_row, end_row, time_format
                    # write the clean value again in the file, if succesful
                    if new_time_value and type(new_time_value) == time_format:
                        ws.cell(row=i_row, column=col).value = new_time_value
                        # if i_row == 2322:
                        #     print "print", new_time_value, "in", i_row, col
                        last_time_value = copy.deepcopy(new_time_value)

                    # value needs to be corected, attempt was unsuccesful
                    else:
                        status_index = False

                if not new_time_value:
                    last_time_value = curr_time_value

            i_row += 1

        return status_index

    @classmethod
    def _clean_values(cls, ws):
        status_data = True

        return status_data

    @classmethod
    def _parse_time(cls, value, time_format):
        # print value

        # time format is correct
        if type(value) == time_format:
            time_value = value

        # fix strings time formats
        elif type(value) == str or type(value) == unicode:
            str_value = value.replace(".", "-").replace("/", "-")
            str_format = "%d-%m-%y"
            time_value = datetime.datetime.strptime(str_value, str_format)

        # no time could be parsed from the value
        else:
            time_value = None

        return time_value

    @classmethod
    def _correct_progression(cls, last_time_value, curr_time_value,
                             freq, missings, missing_value):

        # print last_time_value
        # print last_time_value, curr_time_value, freq
        exp_time_value = cls._increment_time(last_time_value, 1, freq)
        if not exp_time_value:
            msg = "No expected time value could be calcualted from " + \
                str(last_time_value) + " " + str(freq)
            raise Exception(msg)
        # everything is ok!
        if exp_time_value == curr_time_value:
            return curr_time_value

        # going back
        if curr_time_value < last_time_value:
            if cls._time_value_typo(curr_time_value, exp_time_value):
                return exp_time_value
            else:
                return False

        # going forth with no missings allowed
        going_forth = curr_time_value > last_time_value
        if going_forth and not missings:
            try:
                cls._time_value_typo(curr_time_value, exp_time_value)
            except Exception:
                print curr_time_value, exp_time_value, last_time_value

                if cls._time_value_typo(curr_time_value, exp_time_value):
                    return exp_time_value
            else:
                return False

        # going forth with implicit missings
        max_forth_time_value = cls._increment_time(last_time_value,
                                                   cls.MAX_IMPL, freq)
        going_too_forth = curr_time_value > max_forth_time_value
        if going_too_forth and missings and missing_value == "Implicit":
            forth_time_value = cls._forth_time_value_typo(curr_time_value,
                                                          max_forth_time_value)
            if forth_time_value:
                return forth_time_value
            else:
                return False

        # everything should be ok
        else:
            return curr_time_value

    @classmethod
    def _time_value_typo(cls, curr_time_value, exp_time_value):

        matches = [(curr_time_value.day == exp_time_value.day),
                   (curr_time_value.month == exp_time_value.month),
                   (curr_time_value.year == exp_time_value.year)]

        if matches.count(True) == 2:
            return True
        else:
            return False

    @classmethod
    def _forth_time_value_typo(cls, curr_time_value, max_forth_time_value):

        day_typo = datetime.datetime(year=curr_time_value.year,
                                     month=curr_time_value.month,
                                     day=max_forth_time_value.day)

        month_typo = datetime.datetime(year=curr_time_value.year,
                                       month=max_forth_time_value.month,
                                       day=curr_time_value.day)

        year_typo = datetime.datetime(year=max_forth_time_value.year,
                                      month=curr_time_value.month,
                                      day=curr_time_value.day)

        for possible_typo in [day_typo, month_typo, year_typo]:
            if possible_typo < max_forth_time_value:
                return possible_typo

        return None

    # 3. GET DATA methods
    def _get_period_ranges(self, ws):

        period_ranges = []

        for freq, ini_row, header_coord, end_row, time_alignement in \
            zip(self.params.frequency, self.params.data_starts,
                self.params.time_header_coord, self.params.data_ends,
                self.params.time_alignment):

            pr = self._get_period_range(ws, freq, ini_row, header_coord,
                                        end_row, time_alignement)
            period_ranges.append(pr)

        return period_ranges

    def _get_period_range(self, ws, freq, ini_row, header_coord, end_row,
                          time_alignement):
        col = column_index_from_string(ws[header_coord].column)
        period_range = pd.period_range(ws.cell(row=ini_row + time_alignement,
                                               column=col).value,
                                       ws.cell(row=end_row + time_alignement,
                                               column=col).value,
                                       freq=freq)

        return period_range

    def _get_name(self, ws, header_coord):
        return ws[header_coord].value

    def _get_values(self, ws, header_coord, ini_row, end_row):
        col = column_index_from_string(ws[header_coord].column)
        i_series = self.params.headers_coord.index(header_coord)
        continuity = self.params.continuity[i_series]
        missings = self.params.missings[i_series]
        missing_value = self.params.missing_value[i_series]

        values = []
        i_row = ini_row
        while i_row <= end_row:
            value = ws.cell(row=i_row, column=col).value

            new_value = self._handle_new_value(values, value, continuity,
                                               missings, missing_value)
            if new_value:
                values.append(new_value)

            i_row += 1

        # fill the missing values if they are implicit
        if missings and missing_value == "Implicit":
            args = [ws, values, self.params.frequency[i_series],
                    self.params.time_header_coord[i_series],
                    ini_row, end_row]
            values = self._fill_implicit_missings(*args)

        return values

    def _handle_new_value(self, values, value, continuity, missings,
                          missing_value):
        # TODO: use the other parameters to handle the new values

        new_value = None

        if continuity:
            if missings:
                if value != missing_value:
                    args_without_values = locals()
                    del args_without_values["values"]
                    try:
                        new_value = float(value)
                    except:
                        print args_without_values
                        raise Exception("value non valid")
                else:
                    new_value = np.nan
            else:
                new_value = float(value)

        # handles non continuity
        else:
            if missings:
                if value == missing_value:
                    new_value = np.nan
                elif self._valid_value(value):
                    new_value = float(value)
                # values that are not valid nor missings
                else:
                    pass
            else:
                if self._valid_value(value):
                    new_value = float(value)

        return new_value

    def _valid_value(self, value):
        """Check if a value is likely to be a series data value."""

        RV = True

        try:
            float(value)
        except:
            RV = False

        return RV

    @classmethod
    def _fill_implicit_missings(cls, ws, values, frequency, time_header_coord,
                                ini_row, end_row):
        """Fill time holes in the series with missing data."""

        col = column_index_from_string(ws[time_header_coord].column)

        record = []

        new_values = []
        i_value = 0
        i_row = ini_row
        ini_time_value = ws.cell(row=i_row, column=col).value
        exp_time_value = ini_time_value
        while i_row <= end_row:
            obs_time_value = ws.cell(row=i_row, column=col).value
            if i_row == 2322:
                print obs_time_value, exp_time_value

            if type(obs_time_value) != datetime.datetime:
                print "row", i_row, "col", col, obs_time_value

            # if i_row > 100:
            #     break

            # fill time holes in the series with missing data
            while exp_time_value < obs_time_value:
                new_values.append(np.nan)

                record.append(
                    [i_row, col, np.nan, obs_time_value.isoformat(), exp_time_value.isoformat()])

                exp_time_value = cls._increment_time(exp_time_value, 1,
                                                     frequency)

            new_values.append(values[i_value])
            record.append(
                [i_row, col, values[i_value], obs_time_value.isoformat(), exp_time_value.isoformat()])
            exp_time_value = cls._increment_time(exp_time_value, 1, frequency)

            i_row += 1
            i_value += 1

        with open("record.txt", "wb") as f:
            for line in record:
                f.write(str(line) + "\n")

        return new_values

    @classmethod
    def _increment_time(cls, time, num, freq):
        """Return time incremented in "num" times "frequency"."""

        freq_to_time_delta = {"S": "seconds",
                              "T": "minutes",
                              "H": "hours",
                              "D": "days",
                              "W": "weeks",
                              "M": "months",  # not a valid timedelta key
                              "Q": "quarters",  # not a valid timedelta key
                              "Y": "years"}  # not a valid timedelta key

        if freq in freq_to_time_delta:

            if freq not in ["M", "Q", "Y"]:
                time_delta_key = freq_to_time_delta[freq]
                time_delta_dict = {time_delta_key: num}
                time_delta = datetime.timedelta(**time_delta_dict)
                new_time = time + time_delta

            else:
                if freq == "M":
                    new_time = cls._increment_months(time, num)
                elif freq == "Q":
                    new_time = cls._increment_months(time, num * 3)
                elif freq == "Y":
                    new_time = cls._increment_years(time, num)
                else:
                    raise Exception("Unknown frequency")

        else:
            new_time = None

        return new_time

    @classmethod
    def _increment_months(cls, time, num):

        msg = "No time object: " + str(time)
        assert type(time) == datetime.datetime, msg

        month = time.month
        for increment in xrange(num):
            if month == 12:
                month = 1
            else:
                month += 1

        year = time.year + int(num / 12) + int((num % 12 + time.month) / 12)

        return datetime.datetime(year, month, time.day)

    @classmethod
    def _increment_years(cls, time, num):
        return datetime.datetime(time.year + num, time.month, time.day)


def get_parsers_names():
    """Returns a list of the parsers names, whith no Base classes."""

    name = os.path.splitext(os.path.basename(__file__))[0]
    list_cls_names = (pyclbr.readmodule(name).keys())
    list_no_base_cls_names = [cls_name for cls_name in list_cls_names
                              if cls_name[:4] != "Base"]

    return list_no_base_cls_names


def get_parsers():
    """Returns a list of references to the parsers classes."""

    return [globals()[cls_name] for cls_name in get_parsers_names()]


if __name__ == '__main__':
    pprint(sorted(get_parsers_names()))
