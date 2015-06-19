#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import pprint
import copy
from xlseries.utils.xl_methods import xl_coordinates_range

"""
parameters

This module contains the parameters object used by parsing strategies.
"""


class Parameters(object):

    """Object that collects input parameters from parsing strategies."""

    def __init__(self, params=None):

        # general
        self.alignment = None

        # name
        self.series_names = None
        self.headers_coord = None
        self.composed_headers = None

        # data
        self.data_starts = None
        self.data_ends = None
        self.continuity = None
        self.blank_rows = None
        self.multifrequency = None
        self.missings = None
        self.missing_value = None

        # time
        self.time_alignment = None
        self.time_multicolumn = None
        self.time_header = None
        self.time_header_coord = None
        self.time_format = None
        self.time_composed = None
        self.frequency = None

        if params:
            if type(params) == Parameters:
                # self.__dict__ = params.__dict__
                raise Exception("The object passed is already an instance of" +
                                "Parameters.")

            else:
                if type(params) == dict:
                    # add loaded parameters keeping Parameters object defaults
                    loaded_params_dict = self._load_from_dict(params)

                else:
                    # add loaded parameters keeping Parameters object defaults
                    loaded_params_dict = self._load_from_json(params)

                for key, value in loaded_params_dict.items():
                    self.__dict__[key] = value

    def __repr__(self):
        return pprint.pformat(self.__dict__)

    def __getitem__(self, item):

        if type(item) == int:
            return self.get_series_params(item)

        else:
            return self.__getattribute__(item)

    def __iter__(self):
        for param in self.__dict__:
            yield param

    def __setitem__(self, param_name, param_value):
        self.__dict__[param_name] = param_value

    # PUBLIC
    def get_series_params(self, i_series):
        """Returns parameters for only one series."""

        series_params = Parameters()

        for param_name in series_params:

            # when time index is multicolumn, a time_header_coord contains a
            # list of columns composing the multicolumn time index, thus there
            # is no multi-column and multi-index possible in this object, only
            # one "multi" at a time is supported
            if self.time_multicolumn[0] and param_name == "time_header_coord":
                series_params[param_name] = copy.deepcopy(self[param_name])

            else:
                series_params[param_name] = self[param_name][i_series]

        return series_params

    # PRIVATE
    @classmethod
    def _load_from_json(cls, json_params):
        """Load json file parameters into a dictionary."""

        with open(json_params) as f:
            params = json.load(f)
        # print params
        return cls._load_from_dict(params)

    @classmethod
    def _load_from_dict(cls, params):
        """Sanitize parameter inputs in a dict."""

        # convert in lists ranges of headers (eg. "B8-B28")
        if "headers_coord" in params:
            h_c = params["headers_coord"]
            params["headers_coord"] = cls._unpack_header_ranges(h_c)
        else:
            params["headers_coord"] = None

        # convert strings in python expressions
        for param in params:
            params[param] = cls._eval_param(params[param])

        # apply single provided parameters to all series
        num_series = cls._get_num_series(params)
        for param in params:
            if param != "time_header_coord":
                params[param] = cls._apply_to_all(params[param], num_series)
            else:
                params[param] = cls._apply_to_all_time_header(params[param],
                                                              num_series,
                                                              params)

        return params

    @classmethod
    def _eval_param(cls, param):
        """Evaluate a parameter or a list of parameters for expression."""

        if type(param) == list:
            new_list = []
            for elem in param:
                new_list.append(cls._eval_param(elem))

            return new_list

        else:
            try:
                new_param = eval(param)
            except:
                new_param = param

            return new_param

    @classmethod
    def _get_num_series(cls, params):
        """Count number of series present in parameters."""

        num_series = None
        for param in params.values():
            if type(param) == list:
                if not num_series or len(param) > num_series:
                    num_series = len(param)

        return num_series

    @classmethod
    def _apply_to_all(cls, param, num_series):
        """Creates list from single parameter repeating it for every series."""

        if not type(param) == list and num_series:
            param_list = [param for i in xrange(num_series)]

        else:
            param_list = param

        return param_list

    @classmethod
    def _apply_to_all_time_header(cls, param, num_series, params):
        """Creates list from single parameter repeating it for every series."""

        if type(params["time_multicolumn"]) == list:
            time_multicolumn = params["time_multicolumn"][0]
        else:
            time_multicolumn = params["time_multicolumn"]

        if (not type(param) == list or not time_multicolumn):
            return cls._apply_to_all(param, num_series)
        else:
            return [param for i in xrange(num_series)]

    @classmethod
    def _unpack_header_ranges(cls, headers_coord):

        new_list = []

        if type(headers_coord) == list:
            for elem in headers_coord:
                new_list.extend(cls._unpack_header_ranges(elem))

        elif headers_coord.lower() != "none":
            if "-" in headers_coord:
                start, end = headers_coord.upper().split("-")
                new_list = list(xl_coordinates_range(start, end))
            else:
                new_list = [headers_coord.upper()]

        else:
            new_list = None

        return new_list
