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


class InvalidParameter(ValueError):

    """Raised when a parameter is of a non valid value."""

    def __init__(self, param_name, value, valid_values):
        msg = u"""{value} {value_type} is not a valid value for {param_name}
                   parameter. The valid values are {valid_values}.
        """.format(param_name=param_name, value=value,
                   valid_values=valid_values, value_type=type(value))
        super(InvalidParameter, self).__init__(msg)


class Parameters(object):

    """Object that collects input parameters from parsing strategies."""

    VALID_VALUES = {
        "alignment": ["vertical", "horizontal"],
        "series_names": [str, unicode, None],
        "headers_coord": [str, unicode],
        "data_starts": [int],
        "data_ends": [int],
        "continuity": [True, False],
        "blank_rows": [True, False],
        "missings": [True, False],
        "missing_value": [],
        "time_alignment": [int],
        "time_multicolumn": [True, False],
        "time_header_coord": [str, unicode],
        "time_composed": [True, False],
        "frequency": ["Y", "Q", "M", "W", "D"]
    }

    def __init__(self, params=None):

        # general
        self.alignment = None

        # name
        self.series_names = None
        self.headers_coord = None

        # data
        self.data_starts = None
        self.data_ends = None
        self.continuity = None
        self.blank_rows = None
        self.missings = None
        self.missing_value = None

        # time
        self.time_alignment = None
        self.time_multicolumn = None
        self.time_header_coord = None
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
                    if key in self.__dict__:
                        self.__dict__[key] = value
                    else:
                        print key, "parameter is not recognized as valid."

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
    def _load_from_json(cls, json_params):
        """Load json file parameters into a dictionary."""

        with open(json_params) as f:
            params = json.load(f)
        # print params
        return cls._load_from_dict(params)

    @classmethod
    def _load_from_dict(cls, params):
        """Sanitize parameter inputs in a dict."""

        # check that the input is valid
        cls._validate_parameters(params, cls.VALID_VALUES)

        # convert in lists ranges of headers (eg. "B8-B28")
        if "headers_coord" in params:
            h_c = params["headers_coord"]
            params["headers_coord"] = cls._unpack_header_ranges(h_c)
        else:
            params["headers_coord"] = None

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

    @classmethod
    def _validate_parameters(cls, params, valid_values):
        """Check that all values of the parameters are valid."""

        for param_name, param_value in params.iteritems():

            if type(param_value) == list:
                iter_param_values = param_value
            else:
                iter_param_values = [param_value]

            for value in iter_param_values:
                if param_name == "frequency":
                    if not cls._valid_freq(value, valid_values["frequency"]):
                        raise InvalidParameter(param_name, value)

                else:
                    if not cls._valid_param_value(value,
                                                  valid_values[param_name]):
                        raise InvalidParameter(param_name, value,
                                               valid_values[param_name])

    @classmethod
    def _valid_freq(cls, value, valid_values):
        """Check that a frequency is composed of valid frequency characters."""
        for char in value:
            if char not in valid_values:
                return False
        return True

    @classmethod
    def _valid_param_value(cls, value, valid_values):
        """Check that a value is valid.

        Check against a list of valid values or valid types of values."""

        if not valid_values:
            return True

        for valid_value in valid_values:
            if type(valid_value) == type and type(value) == valid_value:
                return True

            elif value == valid_value:
                return True

        return False
