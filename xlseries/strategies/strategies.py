#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
strategies

This module contains the highest level strategies used by `xlseries` to parse
time data series from excel files into Pandas DataFrames.
"""

from __future__ import print_function

from pprint import pprint
import pandas as pd
import numpy as np
import copy

import xlseries.utils.strategies_helpers
from xlseries.strategies.discover.parameters import Parameters
import xlseries.strategies.clean.time_index as clean_ti_strategies
import xlseries.strategies.get.data as get_data_strategies
import xlseries.strategies.get.period_range as get_pr_strategies
from xlseries.utils.data_frame import compare_data_frames
from xlseries.utils.xl_methods import make_ws_copy


# EXCEPTIONS
class TimeIndexNotClean(Exception):

    """Raised if time index of a worksheet could not be cleaned."""
    pass


# STRATEGIES
class BaseXlSeriesScraper(object):

    """Base class for the highest level algorithms of `xlseries`.

    Attributes:
        wb (Workbook): An openpyxl workbook loaded with "data_only=True"
            parameter (this avoids reading formulae).
        params (Parameters): An optional attribute with parameters ready to be
            used in parsing wb. If not passed, the strategy will have to
            discover them or adopt a different approach to parse wb.
    """

    def __init__(self, wb, params_path_or_obj=None, ws_name=None,
                 headers_validation=False):
        self.wb = wb
        self.ws_name = ws_name

        if self.ws_name:
            self.ws = self.wb[self.ws_name]
        else:
            self.ws = self.wb.active

        if isinstance(params_path_or_obj, Parameters):
            self.params = params_path_or_obj
        else:
            self.params = Parameters(params_path_or_obj)

        if headers_validation:
            # remove header coordinates that don't have any cell value (blanks)
            self.params.remove_blank_headers(self.ws)

    # PUBLIC INTERFACE
    @classmethod
    def accepts(cls, wb):
        return cls._accepts(wb)

    def get_data_frames(self, safe_mode):
        return self._get_data_frames(self.ws, self.params, safe_mode)


class ParameterDiscovery(BaseXlSeriesScraper):

    """Scraper that aims to discover and use key parsing parameters.

    The idea in ParameterDiscovery is that Every excel file with time series
    can be safely characterized by a small set of parameters. If the parameters
    are provided, there is a certain way of extracting the time series from
    any file. New cases may need to add small strategies for cleaning values,
    cleaning the time index or getting the clean data, but always using the
    same set of parameters as a way to characterize the excel file.
    """

    # PRIVATE INTERFACE METHODS
    @classmethod
    def _accepts(cls, wb):
        # for the moment, this is the only strategy
        return True

    @classmethod
    def _get_data_frames(cls, ws, params, safe_mode):
        """Extract time data series and return them as data frames."""

        # FIRST: discover missing parameters generating attempts
        attempts = cls._discover_parameters(ws, params)

        # there is only one attempt, probably the user passed all the params
        if len(attempts) == 1:
            params = attempts[0]

            # SECOND: clean the data
            cls._clean_data(ws, params)

            # THIRD: get the data from a cleaned worksheet
            dfs = cls._get_data(ws, params)
            return (dfs, params)

        # there is multiple combinations of parameters to try
        else:
            results = []
            for params_attempt in attempts:
                ws_temp = make_ws_copy(ws)

                try:
                    # SECOND: clean the data
                    cls._clean_data(ws_temp, params_attempt)

                    # THIRD: get the data from a cleaned worksheet
                    dfs = cls._get_data(ws_temp, params_attempt)

                    # don't return a list with only one element
                    if isinstance(dfs, list) and len(dfs) == 1:
                        dfs = dfs[0]
                    if (isinstance(params_attempt, list) and
                            len(params_attempt) == 1):
                        params_attempt = params_attempt[0]

                    results.append((dfs, params_attempt))

                    # stops with the first successful result
                    if not safe_mode:
                        break

                except:
                    continue

            # remove duplicates
            unique_results = []
            for res in results:
                repeated = False  # first result will not be repeated!

                for unique_res in unique_results:
                    repeated = True
                    for df_a, df_b in zip(res[0], unique_res[0]):
                        try:
                            compare_data_frames(df_a, df_b)
                        except AssertionError:
                            repeated = False
                    if repeated:
                        break

                # if True or not repeated:
                if not repeated:
                    unique_results.append(res)

            # return results
            if len(unique_results) == 0:
                raise Exception("""
File couldn't be parsed with provided parameters:
{}

Last attempt was:
{}
""".format(repr(params), repr(params_attempt)))
            elif len(unique_results) == 1:
                return unique_results[0]

            else:
                print("There is more than one result with given parameters.")
                dfs = [res[0] for res in unique_results]
                params = [res[1] for res in unique_results]
                return (dfs, params_attempt)

    # HIGH LEVEL TASKS
    @classmethod
    def _discover_parameters(cls, ws, params):
        """Discover the parameters of the worksheet."""

        if not params.is_complete():
            non_discovered = cls._discover_missing_params(params)

            if non_discovered:
                return cls._generate_attempts(non_discovered, params)
            else:
                return [params]
        else:
            return [params]

    @classmethod
    def _clean_data(cls, ws, params):
        """Ensure data is clean to be processed with the parameters."""

        # 1. Clean time index

        # if time index is multicolumn, only one time index is allowed
        if params["time_multicolumn"][0]:
            end = cls._clean_time_index(ws, params[0])

            # if not provided, the end is when time index finish
            if not params["data_ends"][0]:
                params["data_ends"] = end

        # if time index is not multicolumn, many time indexes are allowed
        else:
            time_indexes_ends = {}
            time_indexes = set()
            for i_series in range(len(params.time_header_coord)):

                # avoid cleaning the same time index twice
                time_header_coord = params["time_header_coord"][i_series]
                if time_header_coord not in time_indexes:
                    time_indexes.add(time_header_coord)
                    end = cls._clean_time_index(ws, params[i_series])
                    assert end, "Clean time index should have an end."
                    time_indexes_ends[time_header_coord] = end

                # if not provided, the end is when time index finish
                if not params["data_ends"][i_series]:
                    # start = params["data_starts"][i_series]

                    # for i_series in xrange(len(params.time_header_coord)):
                    #     if params["data_starts"][i_series] == start:
                    params["data_ends"][i_series] = time_indexes_ends[
                        time_header_coord]

        # 2. Clean data values
        for i_series in range(len(params.headers_coord)):
            cls._clean_values(ws)

    @classmethod
    def _get_data(cls, ws, params):
        """Parse data using parameters and return it in data frames."""
        # import pdb; pdb.set_trace()
        # 1. Build data frames dict based on number of period ranges founded
        dfs_dict = {}
        for period_range in cls._get_period_ranges(ws, params):
            hashable_pr = cls._hash_period_range(period_range)
            if hashable_pr not in dfs_dict:
                dfs_dict[hashable_pr] = {"columns": [], "data": [],
                                         "period_range": period_range}

        # 2. Get name (column) and values of each data series
        for i_series in range(len(params.headers_coord)):

            # iterate strategies looking for someone that accepts it
            params_series = params[i_series]
            name, values = None, None
            for strategy in get_data_strategies.get_strategies():

                if strategy.accepts(ws, params_series):
                    strategy_obj = strategy()
                    # import pdb; pdb.set_trace()
                    names_and_values = strategy_obj.get_data(ws, params_series)
                    names, values = names_and_values[0]
                    break

            # raise exception if no strategy accepts the input
            if not names_and_values:
                msg = "There is no strategy to deal with " + str(params_series)
                raise Exception(msg)

            if (params_series["time_multicolumn"] and
                    isinstance(params_series["time_header_coord"], list)):
                time_header_coord = params_series["time_header_coord"][0]
            else:
                time_header_coord = params_series["time_header_coord"]

            prs = cls._get_series_prs(ws, params_series["frequency"],
                                      params_series["data_starts"],
                                      time_header_coord,
                                      params_series["data_ends"],
                                      params_series["time_alignment"],
                                      params_series["alignment"])

            for period_range, (name, values) in zip(prs, names_and_values):
                hashable_pr = cls._hash_period_range(period_range)

                cls._add_name(name, dfs_dict[hashable_pr]["columns"])
                dfs_dict[hashable_pr]["data"].append(values)

        # 3. Build data frames
        dfs = []
        for df_inputs in list(dfs_dict.values()):

            period_range = df_inputs["period_range"]
            columns = df_inputs["columns"]
            data = np.array(df_inputs["data"]).transpose()

            # try with business days if daily frequency fails
            if period_range.freqstr == "D":
                try:
                    df = pd.DataFrame(index=period_range,
                                      columns=columns,
                                      data=data)
                except ValueError:
                    # rework period range in business days
                    pr = period_range
                    ini_date = "{}-{}-{}".format(pr[0].year,
                                                 pr[0].month, pr[0].day)
                    end_date = "{}-{}-{}".format(pr[-1].year,
                                                 pr[-1].month, pr[-1].day)
                    pr_B = pd.period_range(ini_date, end_date, freq="B")

                    df = pd.DataFrame(index=pr_B,
                                      columns=columns,
                                      data=data)

            # go straight if frequency is not daily
            else:
                df = pd.DataFrame(index=period_range,
                                  columns=columns,
                                  data=data)

            dfs.append(df)

        return dfs

    # auxiliar methods
    @staticmethod
    def _hash_period_range(period_range):
        """Returns a tuple describing a period range in a hashable way."""
        return period_range.freqstr, period_range[0], period_range[-1]

    # 1. DISCOVER PARAMETERS methods
    @classmethod
    def _discover_missing_params(cls, params):
        """This method would call strategies to discover some of the missing
        parameters, but for now it just return them all."""
        return params.get_missings()

    @classmethod
    def _generate_attempts(cls, non_discovered, params):
        """Generate combinations of the valid values of non discovered missing
        parameters and create attempts of parameters to try scrape the file."""

        # no missings? only one attempt then!
        if not non_discovered:
            return [params]

        missings_dict = {missing_param: params.VALID_VALUES[missing_param]
                         for missing_param in non_discovered}

        attempts = []
        for combination in cls._param_combinations_generator(
                missings_dict, params.DEFAULT_VALUES, params.LIKELINESS_ORDER):
            new_params = copy.deepcopy(params)

            for param_name, param_value in combination.items():
                new_params[param_name] = param_value

            msg = repr(new_params) + \
                " is not complete.\nMissing parameters " + \
                repr(new_params.get_missings())
            assert new_params.is_complete(), msg

            attempts.append(new_params)

        return attempts

    @classmethod
    def _param_combinations_generator(cls, missings_dict, default_values=None,
                                      likeliness_order=None):
        """Generator of valid values combinations of missing parameters.

        Args:
            missings_dict (dict): {missing_parameter: valid_values_of_it}
            default_values (dict): {parameter_name: default_value}
            likeliness_order (list): Parameters ordered by likeliness of their
                default value.
        """
        missings_dict_c = missings_dict.copy()

        if len(missings_dict_c) == 1:
            missing_param, valid_values = missings_dict_c.popitem()
            valid_values_c = copy.deepcopy(valid_values)

            if len(valid_values_c) == 0:
                if default_values:
                    valid_values_c = [default_values[missing_param]]
                else:
                    msg = "A default value for " + missing_param + \
                        " is required."
                    raise Exception(msg)

            # yield default value first
            if default_values:
                index = valid_values_c.index(default_values[missing_param])
                valid_value = valid_values_c.pop(index)
                yield {missing_param: valid_value}

            for valid_value in valid_values_c:
                yield {missing_param: valid_value}

        else:
            if not likeliness_order:
                missing_param, valid_values = missings_dict_c.popitem()
                likeliness_order_c = None

                if len(valid_values) == 0:
                    if default_values:
                        valid_values = [default_values[missing_param]]
                    else:
                        msg = "A default value for " + missing_param + \
                            " is required."
                        raise Exception(msg)

            else:
                likeliness_order_c = copy.deepcopy(likeliness_order)
                missing_param = likeliness_order_c.pop()

                while missing_param not in missings_dict_c:
                    missing_param = likeliness_order_c.pop(0)

                valid_values = missings_dict_c[missing_param]
                del missings_dict_c[missing_param]

                if len(valid_values) == 0:
                    if default_values:
                        valid_values = [default_values[missing_param]]
                    else:
                        msg = "A default value for " + missing_param + \
                            " is required."
                        raise Exception(msg)

            for comb in cls._param_combinations_generator(missings_dict_c,
                                                          default_values,
                                                          likeliness_order_c):

                # yield default value first
                valid_values_c = copy.deepcopy(valid_values)
                if default_values:
                    index = valid_values_c.index(default_values[missing_param])
                    valid_value = valid_values_c.pop(index)
                    new_comb = comb.copy()
                    new_comb[missing_param] = valid_value
                    yield new_comb

                for valid_value in valid_values_c:
                    new_comb = comb.copy()
                    new_comb[missing_param] = valid_value
                    yield new_comb

    # 2. CLEAN DATA methods
    @classmethod
    def _clean_time_index(cls, ws, params):
        """Clean time index from strings, typos and errors.

        Modify ws changing cell values in the time index for the correspondent
        time value in datetime.datetime format."""

        for cleaner in clean_ti_strategies.get_strategies():
            if cleaner.accepts(ws, params):
                cleaner_obj = cleaner()
                return cleaner_obj.clean_time_index(ws, params)

        msg = "Time index in '" + ws.title + "'' could not be cleaned."
        raise TimeIndexNotClean(msg)

    @classmethod
    def _clean_values(cls, ws):
        """TODO: This method should clean the missing values, instead of
        leaving that burden to get data methods..."""
        pass

    # 3. GET DATA methods
    @classmethod
    def _get_period_ranges(cls, ws, params):
        """Get period ranges for all series in the worksheet.

        Args:
            ws (Worksheet): A clean worksheet with time values in its time
                index.
            freq (str): Frequency (Y, Q, M, D, YQQQQ...).
            ini (int): Row or column where data starts.
            time_header_coord (str): Coordinate of the first cell that would be
                the header of the time index ("A1") even if it hasn't got an
                explicit header name.
            end (int): Row or column where data ends.
            time_alignement (int): Indicates if data runs parallel to the time
                index or is offset (-1, 0 or 1).
            alignment (str): "vertical" or "horizontal" series.
        """

        for (freq, ini_row, time_header_coord, end_row, time_alignement,
             alignment) in \
            zip(params.frequency, params.data_starts,
                params.time_header_coord, params.data_ends,
                params.time_alignment, params.alignment):

            msg = "No end could be estimated! End: {} | Start: {}".format(
                repr(end_row).ljust(6), ini_row
            )
            assert end_row and end_row > ini_row, msg

            # if time is multicolumn, pass only the first column
            if params.time_multicolumn and isinstance(time_header_coord, list):
                time_header_coord_single = time_header_coord[0]
            else:
                time_header_coord_single = time_header_coord

            for pr in cls._get_series_prs(ws, freq, ini_row,
                                          time_header_coord_single,
                                          end_row, time_alignement,
                                          alignment):
                yield pr

    @classmethod
    def _get_series_prs(cls, ws, freq, ini_row, time_header_coord, end_row,
                        time_alignement, alignment):
        """Get the period ranges of one time index.

        In single frequency series this would be just one period range. In
        multifrequency series this would be one perior range for each single
        frequency.

        Args:
            ws (Worksheet): A clean worksheet with time values in its time
                index.
            freq (str): Frequency (Y, Q, M, D, YQQQQ...).
            ini (int): Row or column where data starts.
            time_header_coord (str): Coordinate of the first cell that would be
                the header of the time index ("A1") even if it hasn't got an
                explicit header name.
            end (int): Row or column where data ends.
            time_alignement (int): Indicates if data runs parallel to the time
                index or is offset (-1, 0 or 1).
            alignment (str): "vertical" or "horizontal" series.
        """

        for strategy in get_pr_strategies.get_strategies():
            if strategy.accepts(ws, freq):
                return strategy.get_period_ranges(ws, freq, ini_row,
                                                  time_header_coord, end_row,
                                                  time_alignement,
                                                  alignment)

        msg = " ".join(["There is no strategy to get period range for",
                        "\nFrequency:", freq,
                        "\nTime header coord:", time_header_coord])
        raise Exception(msg)

    @classmethod
    def _add_name(cls, name, columns, index=1):
        """Add a new name to the data frame columns.

        If name is repeated, and index number is added an incremented until the
        name is not repeated any more.

        Args:
            name (str): Field name.
            columns (list): Fields of the data frame.
            index (int): Index number for repeated fields.
        """
        if cls._indexed_name(name, index) not in columns:
            columns.append(cls._indexed_name(name, index))
        else:
            cls._add_name(name, columns, index + 1)

    @classmethod
    def _indexed_name(cls, name, index):
        """Return and indexed name."""
        if index <= 1:
            return name
        else:
            return name + "." + str(index)


def get_strategies():
    return xlseries.utils.strategies_helpers.get_strategies()


if __name__ == '__main__':
    pprint(sorted(xlseries.utils.strategies_helpers.get_strategies_names()))
