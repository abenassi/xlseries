#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import datetime
import pprint
import re
from xlseries.utils.xl_methods import xl_coordinates_range

"""
parameters
----------------------------------

This module contains the parameters object used by parsing strategies.

TODO: "B8-B28" should be parsed into a list from 8 to 28. Handle cols too.
"""


class Parameters(object):

    """Object that collects input parameters from parsing strategies."""

    def __init__(self, json_params_file=None):

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
        self.progressive_aggregation = None

        # time
        self.time_alignment = None
        self.time_multicolumn = None
        self.time_header = None
        self.time_header_coord = None
        self.time_header_next_to_data = None
        self.time_format = None
        self.time_composed = None
        self.frequency = None

        if json_params_file:
            if type(json_params_file) == Parameters:
                self.__dict__ = json_params_file.__dict__
                # raise Exception(self)
            else:
                self.__dict__ = self._load_parameters(json_params_file)

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
            series_params[param_name] = self[param_name][i_series]

        return series_params

    # PRIVATE
    @classmethod
    def _load_parameters(cls, json_params_file):
        """Load json file parameters into a dictionary."""

        with open(json_params_file) as f:
            params = json.load(f)

        # convert in lists ranges of headers (eg. "B8-B28")
        h_c = params["headers_coord"]
        params["headers_coord"] = cls._unpack_header_ranges(h_c)

        # convert strings in python expressions
        for param in params:
            params[param] = cls._eval_param(params[param])

        # apply single provided parameters to all series
        num_series = cls._get_num_series(params)
        for param in params:
            params[param] = cls._apply_to_all(params[param], num_series)

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

        num_series = 1
        for param in params.values():
            if type(param) == list and len(param) > num_series:
                num_series = len(param)

        return num_series

    @classmethod
    def _apply_to_all(cls, param, num_series):
        """Creates list from single parameter repeating it for every series."""

        if not type(param) == list and num_series > 1:
            param_list = [param for i in range(num_series)]

        else:
            param_list = param

        return param_list

    @classmethod
    def _unpack_header_ranges(cls, headers_coord):

        new_list = []

        if type(headers_coord) == list:
            for elem in headers_coord:
                new_list.extend(cls._unpack_header_ranges(elem))

        else:
            if "-" in headers_coord:
                start, end = headers_coord.upper().split("-")
                new_list = list(xl_coordinates_range(start, end))
            else:
                new_list = [headers_coord.upper()]

        return new_list
