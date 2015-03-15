#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import datetime
import pprint

"""
parameters
----------------------------------

This module contains the parameters object used by parsing strategies.
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
        self.missings_format = None
        self.progressive_aggregation = None

        # time
        self.time_header = None
        self.time_header_coord = None
        self.time_header_next_to_data = None
        self.time_format = None
        self.time_composed = None
        self.frequency = None

        if json_params_file:
            self.__dict__ = self._load_parameters(json_params_file)

    def __repr__(self):
        return pprint.pformat(self.__dict__)

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def _load_parameters(self, json_params_file):

        with open(json_params_file) as f:
            params = json.load(f)

        for param in params:

            if params[param] == u"None":
                params[param] = None
            elif params[param] == u"True":
                params[param] = True
            elif params[param] == u"False":
                params[param] = False
            elif params[param] == u"datetime.datetime":
                params[param] = datetime.datetime
            else:
                pass

        return params
