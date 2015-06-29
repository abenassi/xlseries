#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import pprint
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


class CriticalParameterMissing(Exception):

    """Raised when a critical parameter is not provided by the user."""

    def __init__(self, param_name):
        msg = u"{param_name} is a critical parameter. It has to be " + \
            "provided by the user.".format(param_name=param_name)
        super(CriticalParameterMissing, self).__init__(msg)


class Parameters(object):

    """Object that collects input parameters from parsing strategies."""

    VALID_VALUES = {
        "alignment": [u"vertical", u"horizontal"],
        "series_names": [str, unicode, None],
        "headers_coord": [str, unicode],
        "data_starts": [int],
        "data_ends": [int, None],
        "continuity": [True, False],
        "blank_rows": [True, False],
        "missings": [True, False],
        "missing_value": [],
        "time_alignment": [-1, 0, 1],
        "time_multicolumn": [True, False],
        "time_header_coord": [str, unicode],
        "time_composed": [True, False],
        "frequency": ["Y", "Q", "M", "W", "D"]
    }

    DEFAULT_VALUES = {
        "alignment": u"vertical",
        "continuity": True,
        "blank_rows": False,
        "missings": False,
        "missing_value": None,
        "time_alignment": 0,
        "time_multicolumn": False,
        "time_composed": False,
        "data_ends": None,
        "series_names": None
    }

    LIKELINESS_ORDER = ["time_alignment", "alignment", "continuity",
                        "blank_rows", "missings", "time_multicolumn",
                        "time_composed"]

    CRITICAL = ["headers_coord", "data_starts",
                "time_header_coord", "frequency"]

    OPTIONAL = ["series_names", "data_ends"]

    USE_DEFAULT = ["time_alignment"]

    TYPE_PARAMETERS = "<class 'xlseries.strategies.discover.parameters.Parameters'>"

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
            if (type(params) == Parameters or
                    unicode(type(params)) == self.TYPE_PARAMETERS):
                # add loaded parameters keeping Parameters object defaults
                loaded_params_dict = self._load_from_dict(params.__dict__)

            elif type(params) == dict:
                # add loaded parameters keeping Parameters object defaults
                loaded_params_dict = self._load_from_dict(params)

            elif ((type(params) == str or type(params) == unicode) and
                  params[-4:] == "json"):
                # add loaded parameters keeping Parameters object defaults
                loaded_params_dict = self._load_from_json(params)

            else:
                print type(params)
                msg = repr(params) + unicode(type(params)) + "not recognized."
                raise Exception(msg)

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
        num_series = self._get_num_series(self.__dict__)
        if self._valid_param_list(param_name, param_value, num_series):
            self.__dict__[param_name] = param_value

        else:
            if not self._valid_param_value(param_value,
                                           self.VALID_VALUES[param_name]):
                raise InvalidParameter(param_name, param_value,
                                       self.VALID_VALUES[param_name])

            self.__dict__[param_name] = self._apply_to_all(
                param_name, param_value, self._get_num_series(
                    self.__dict__), self,
                self.VALID_VALUES[param_name])

    def __eq__(self, other):
        for key in self:
            if self[key] != other[key]:
                return False

        for key in other:
            if self[key] != other[key]:
                return False

        return True

    # PUBLIC
    def get_series_params(self, i_series):
        """Returns parameters for only one series."""

        series_params = Parameters().__dict__

        for param_name in series_params.keys():
            if self[param_name] is not None:
                series_params[param_name] = self[param_name][i_series]

            # missing parameters have to be deleted from slicing so they are
            # not confused with possible valid None values
            else:
                del series_params[param_name]

        return series_params

    def is_complete(self):
        """Check if all the parameters have values (ie. no misssing params)."""
        num_series = self._get_num_series(self.__dict__)

        for param_name in self:
            if (param_name not in self.OPTIONAL and
                (self[param_name] is None or
                 len(self[param_name]) != num_series)):
                return False

        return True

    def get_missings(self):
        """Return the names of parameters that were not passed by the user."""
        missings = []
        for param in self:
            if self._is_missing(param):
                missings.append(param)
        return missings

    def get_non_critical_params(self, differents=True):
        """Return the name of non critical parameters.

        Args:
            differents (bool): If True, will also get non critical parameters
                that have differences across series.
        """
        if not differents:
            return [param for param in self if (self._non_critical(param) and
                                                self._no_differences(param))]
        else:
            return [param for param in self if self._non_critical(param)]

    def num_missings(self):
        """Return the number of missing parameters."""
        return sum((1 for param in self if self._is_missing(param)))

    def remove_non_critical(self, differents=False):
        """Remove all non critical parameters."""
        map(self.remove, self.get_non_critical_params(differents))

        # restore optionals
        for optional_param in self.OPTIONAL:
            self[optional_param] = None

        # restore defaults
        self._missings_to_default(self)

    def remove(self, param):
        """Remove a parameters setting it to 'missing'."""
        self.__dict__[param] = None

    # PRIVATE
    def _valid_param_list(self, param_name, param_value, num_series):
        """Return True if param_value is a valid list of parameters for
        param_name."""
        return (type(param_value) == list and
                len(param_value) == num_series and
                all(self._valid_param_value(param,
                                            self.VALID_VALUES[param_name])
                    for param in param_value)
                )

    def _non_critical(self, param):
        """Return True if param is not critical."""
        return param not in self.CRITICAL

    def _no_differences(self, param):
        """Return True if param is the same for all the series."""
        if type(self[param]) == list:
            return len(set(self[param])) == 1
        else:
            return True

    def _is_missing(self, param):
        valid_values = self.VALID_VALUES[param]
        return (self[param] is None and None not in valid_values)

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

        # ensure critical parameters
        cls._ensure_critical_parameters(params, cls.CRITICAL, cls.VALID_VALUES)

        # check that the input is valid
        cls._validate_parameters(params, cls.VALID_VALUES)

        cls._missings_to_default(params)

        # convert in lists ranges of headers (eg. "B8-B28")
        if "headers_coord" in params:
            h_c = params["headers_coord"]
            params["headers_coord"] = cls._unpack_header_ranges(h_c)
        else:
            params["headers_coord"] = None

        # apply single provided parameters to all series
        num_series = cls._get_num_series(params)
        for param_name in params:
            params[param_name] = cls._apply_to_all(
                param_name, params[param_name], num_series, params,
                cls.VALID_VALUES[param_name])

        # apply Nones to optional parameters
        for param_name in cls.OPTIONAL:
            if param_name not in params or not params[param_name]:
                params[param_name] = cls._apply_to_all(
                    param_name, cls.DEFAULT_VALUES[param_name], num_series,
                    params, cls.VALID_VALUES[param_name])

        return params

    @classmethod
    def _missings_to_default(cls, params):
        """Set missing parameters in the USE_DEFAULT list to their defaults.

        These parameters, when not provided by the user, will use their
        defaults rather than stay missing to be guessed by the package in a
        later stage."""

        for use_default in cls.USE_DEFAULT:
            if ((use_default not in params or params[use_default] is None) and
                    None not in cls.VALID_VALUES[use_default]):
                params[use_default] = cls.DEFAULT_VALUES[use_default]

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
    def _apply_to_all(cls, param_name, param_value, num_series, params,
                      valid_values=None):
        """Creates list from single parameter repeating it for every series."""

        if param_name == "time_header_coord":
            return cls._apply_to_all_time_header(param_value, num_series,
                                                 params, valid_values)

        if (param_value is None and valid_values and None not in valid_values):
            return None

        elif not type(param_value) == list and num_series:
            param_list = [param_value for i in xrange(num_series)]

        else:
            param_list = param_value

        return param_list

    @classmethod
    def _apply_to_all_time_header(cls, param, num_series, params,
                                  valid_values=None):
        """Creates list from single parameter repeating it for every series."""

        if "time_multicolumn" not in params:
            time_multicolumn = cls.DEFAULT_VALUES["time_multicolumn"]
        elif type(params["time_multicolumn"]) == list:
            time_multicolumn = params["time_multicolumn"][0]
        else:
            time_multicolumn = params["time_multicolumn"]

        if (not type(param) == list or not time_multicolumn):
            return cls._apply_to_all("", param, num_series,
                                     params, valid_values)
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

            # if a parameter is not provided, its validity cannot be checked
            if param_value is None:
                continue

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

    @classmethod
    def _ensure_critical_parameters(cls, params, critical, valid_values):
        for param_name, param_value in params.iteritems():
            if (param_value is None and param_name in critical and
                    None not in valid_values[param_name]):
                raise CriticalParameterMissing(param_name)
