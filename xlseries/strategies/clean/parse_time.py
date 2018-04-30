#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
parse_time

This module contains strategies to parse time strings of different frequencies.
Up to this momment, all the strategies need to know the frequency of the time
string in advance (yearly, quarterly, monthly..)

The preconditions of all the strategies is that the strings passed to them must
be time values, otherwise an exception will be raised.
"""

from pprint import pprint
import arrow
import datetime
import parsley
import collections
from unidecode import unidecode
import sys

from xlseries.utils.time_manipulation import increment_time
import xlseries.utils.strategies_helpers

PYTHON2 = sys.version_info[0] == 2

# EXCEPTIONS


class NoPossibleTimeValue(ValueError):

    """Raised if the value is not a possible time value."""

    def __init__(self, value):
        msg = " ".join([str(type(value)), str(value),
                        "is not a possible time value."])
        super(NoPossibleTimeValue, self).__init__(msg)


class TimeIsNotComposed(ValueError):

    """Raised if a valid time value try to be parsed as composed.

    If a spreadsheet has time values already, time_composed parameter should be
    False."""

    def __init__(self, value):
        msg = " ".join([str(type(value)), str(value),
                        "is not a composed time, time_composed should be set"
                        "False."])
        super(TimeIsNotComposed, self).__init__(msg)


class NoTimeValue(ValueError):

    """Raised if the value is not an arrow.Arrow time value."""

    def __init__(self, value, last_time=None, next_time=None):
        msg = " ".join([str(type(value)), str(value),
                        "is not an arrow.Arrow time value."])
        if last_time:
            msg += "\nLast:" + str(last_time)
        if next_time:
            msg += "\nNext:" + str(next_time)

        super(NoTimeValue, self).__init__(msg)


class BaseDateMemberOutOfRange(ValueError):

    """Part of the result of a parsing grammar is out of range for a date."""

    def __init__(self, curr_time, grammar_result):
        msg = " ".join(["Time value doesn't make sense.",
                        str(curr_time), "has been converted into",
                        str(grammar_result)])
        super(BaseDateMemberOutOfRange, self).__init__(msg)


class DayOutOfRange(BaseDateMemberOutOfRange):

    """Raised if a day in a parsed time value is out of range."""


class MonthOutOfRange(BaseDateMemberOutOfRange):

    """Raised if a month in a parsed time value is out of range."""


# STRATEGIES
class BaseParseTimeStrategy(object):

    """BaseParseTimeStrategy class for all parse time strategies."""

    # PUBLIC INTERFACE
    @classmethod
    def accepts(cls, params, curr_time, last_time=None, next_time=None):
        """Check the inputs to see if the strategy can handle them.

        This base accepts() method check that the value is either already a
        time value or that could be a string expressing time before. In the
        latter it will call the private _accepts() method of the concrete
        strategy being called to see if it can be handled.

        Args:
            params: Parameters of the series being analyzed.
            curr_time: Value to be parsed into a date format.
            last_time: Last value parsed into time value.
            next_time: Next value to be parsed into time value.

        Returns:
            True or False meaning that a strategy declares it can handle the
                input.
        """
        # import pdb; pdb.set_trace()
        if isinstance(curr_time, str) or isinstance(curr_time, str):
            curr_time = unidecode(curr_time).strip()

        if cls._already_time_value(curr_time):
            if params["time_composed"]:
                raise TimeIsNotComposed(curr_time)
            else:
                return True
        else:
            if not cls._possible_time_value(curr_time):
                raise NoPossibleTimeValue(curr_time)

            if not (isinstance(last_time, arrow.Arrow) or last_time is None):
                raise NoTimeValue(last_time)

            if isinstance(curr_time, float):
                float_to_uni = cls._accepts(params, str(curr_time),
                                            last_time, next_time)
                float_to_int = cls._accepts(params, str(int(curr_time)),
                                            last_time, next_time)
                # print float_to_uni, float_to_int
                return float_to_uni or float_to_int
            else:
                return cls._accepts(params, str(curr_time), last_time,
                                    next_time)

    def parse_time(self, params, curr_time, last_time=None, next_time=None):
        """Parse a time string or value into a proper time value.

        Args:
            params: Parameters of the series being analyzed.
            curr_time: Value to be parsed into a date format.
            last_time: Last value parsed into time value.
            next_time: Next value to be parsed into time value.

        Returns:
            An arrow.Arrow time value.
        """
        if isinstance(curr_time, str):
            curr_time = unidecode(curr_time).strip()

        # time format is correct
        if isinstance(curr_time, arrow.Arrow):
            RV = curr_time

        elif isinstance(curr_time, datetime.datetime):
            RV = arrow.get(curr_time)

        elif (isinstance(curr_time, str) or
              isinstance(curr_time, int) or
              (PYTHON2 and isinstance(curr_time, long))):
            RV = self._parse_time(params, str(curr_time), last_time,
                                  next_time)
        elif isinstance(curr_time, float):
            try:
                RV = self._parse_time(params, str(int(curr_time)),
                                      last_time, next_time)
            except:
                RV = self._parse_time(params, str(curr_time),
                                      last_time, next_time)
        else:
            assert isinstance(curr_time, str), "Current is not unicode."

            time_value = self._parse_time(params, curr_time,
                                          last_time, next_time)

            if not isinstance(time_value, arrow.Arrow):
                raise NoTimeValue(time_value, last_time, next_time)

            RV = time_value

        return RV

    def _parse_time(self, params, curr_time, last_time=None, next_time=None):
        """Base _parse_time() method.

        Most of the concrete strategies subclassing BaseParseTimeStrategy will
        use this method and override only make_parsley_grammar() to change the
        grammar actually used to parse a time string. If the structure varies
        significantly or can be simpler, the entire _parse_time() method should
        be overriden.

        Args:
            curr_time: Time string to be parsed.
            last_time: Last time value (already parsed) in the time series
                being analyzed.
            params: A parameters dictionary with meta-data about the series
                being analyzed.

        Returns:
            An arrow.Arrow time value.
        """

        result = self._parse_date_elements(curr_time)

        year, month, day = self._fill_parse_date_holes(result, last_time)

        # check date make sense
        if day not in list(range(1, 32)):
            raise DayOutOfRange(curr_time, result)

        if month not in list(range(1, 13)):
            raise MonthOutOfRange(curr_time, result)

        return arrow.get(year, month, day)

    @staticmethod
    def _dob_year_to_four(dob_year):
        """Convert a two digit year string in a four digits year string."""
        if not dob_year:
            return None

        if isinstance(dob_year, str) or isinstance(dob_year, str):
            if len(dob_year) == 4:
                return int(dob_year)
            else:
                return arrow.Arrow.strptime(dob_year, "%y").year
        else:
            return int(dob_year)

    @classmethod
    def _already_time_value(cls, value):
        """Check if a value is already of a time value type."""
        return (isinstance(value, arrow.Arrow) or isinstance(value, datetime.datetime))

    @classmethod
    def _possible_time_value(cls, value):
        """Check that a value could be a time value."""
        return (value is not None)

    @classmethod
    def _parse_date_elements(cls, curr_time):
        """Parse any date elements found in curr_time.

        Args:
            curr_time (str): String time to be parsed.

        Returns:
            tuple: (year, month, day) At least one element is not None, but the
                others could be None.
        """
        raise NotImplementedError("This method is implemented in subclasses.")

    @classmethod
    def _fill_parse_date_holes(cls, result, last_time):
        """Analyze parsed result with last time to complete missings.

        Every missing is replaced with the value of the last time value.

        Args:
            result (tuple): (year, month, day) Each element could be an integer
                or None.
            last_time (arrow.Arrow): Last time value parsed.

        Returns:
            tuple: (year, month, day) All the elements are integers, providing
                all the information to create a new time value.
        """

        # take new date elements found with the grammar
        if last_time:
            year = int(result[0] or last_time.year)
            month = int(result[1] or last_time.month)
            day = int(result[2] or last_time.day)
        else:
            year = int(result[0] or 1)
            month = int(result[1] or 1)
            day = int(result[2] or 1)

        return year, month, day


class ParseSimpleTime(BaseParseTimeStrategy):

    """Parse dates expressed in a standard or very easy string to parse."""
    MAX_IMPL = 20

    def __init__(self, time_format=None):
        self.time_format = time_format

    @classmethod
    def _accepts(cls, params, curr_time, last_time=None, next_time=None):
        return not params["time_composed"]

    def _parse_time(self, params, curr_time, last_time=None, next_time=None):
        """Parse a string into a time value.

        Try different standard formats and check that the result make sense in
        the progression of the time series."""

        str_value = curr_time.replace(".", "-").replace("/", "-")
        time_value = None

        # first try with the last time format that worked
        if self.time_format:
            try:
                time_value = arrow.get(str_value, self.time_format)
                if not self._time_make_sense(params, time_value, last_time,
                                             next_time):
                    time_value = None

                if not isinstance(time_value, arrow.Arrow):
                    raise NoTimeValue(time_value, last_time, next_time)

                return time_value

            except:
                pass

        # if it doesn't work, try with everyone
        formats = list(self._get_possible_time_formats(str_value))
        for time_format in formats:
            try:
                time_value = arrow.get(str_value, time_format)
            except Exception:
                continue

            if not self._time_make_sense(params, time_value, last_time,
                                         next_time):
                time_value = None
                continue

            else:
                break

        if not isinstance(time_value, arrow.Arrow):
            raise NoTimeValue(time_value, last_time, next_time)

        return time_value

    def _time_make_sense(self, params, time_value, last_time, next_time):
        """Check that a parsed time value make sense with the previous one.

        Args:
            params: Parameters of the time series.
            time_value: Recently parsed time value.
            last_time: Last time value that was parsed.
            next_time: Next value to be parsed into a time value.

        Returns:
            True or False, if the value make sense with the last one and the
                next one.
        """

        # making sense with the last value
        if last_time:
            is_after_last = time_value > last_time
            max_forth_time_value = increment_time(last_time, self.MAX_IMPL,
                                                  params["frequency"])
            is_not_too_after_last = time_value <= max_forth_time_value

        else:
            is_after_last, is_not_too_after_last = True, True

        # making sense with the next value
        if next_time:
            try:
                next_time = self.parse_time(params, next_time, time_value)
                is_before_next = time_value < next_time
                max_forth_time_value = increment_time(time_value,
                                                      self.MAX_IMPL,
                                                      params["frequency"])
                is_not_too_before_next = next_time <= max_forth_time_value

            except NoTimeValue:
                is_before_next, is_not_too_before_next = False, False

        else:
            is_before_next, is_not_too_before_next = True, True

        return (is_after_last and is_not_too_after_last and is_before_next and
                is_not_too_before_next)

    @staticmethod
    def _get_possible_time_formats(str_value):
        """Generate all possible time formats that could apply to str_value.

        Args:
            str_value: A string representing time.

        Yields:
            A possible time format for a given time string value.
        """

        reps = list(map(len, str_value.split("-")))
        assert len(reps) == 3, "There is no 3 date elements in " + str_value

        for order in ["D-M-Y", "M-D-Y", "Y-M-D"]:
            time_format = "-".join([char * reps[i] for i, char in
                                    enumerate(order.split("-"))])
            yield time_format


class BasePEG(BaseParseTimeStrategy):

    def __init__(self):
        self.grammar = None

    def _parse_date_elements(self, curr_time):
        """Parse any date elements found in curr_time.

        Args:
            curr_time (str): String time to be parsed.

        Returns:
            tuple: (year, month, day) At least one element is not None, but the
                others could be None.
        """

        # create grammar only if not already created
        if not self.grammar:
            self.grammar = self.make_parsley_grammar()

        return self.grammar(curr_time).date()


class BaseComposedQuarter():

    """Parse dates from strings composed by substrings with date info.
    Only for quarterly series."""

    @classmethod
    def _accepts(cls, params, curr_time, last_time=None, next_time=None):

        if params["time_composed"] and params["frequency"] == "Q":
            try:
                cls.make_parsley_grammar()(curr_time).date()
            except:
                return False
            return True
        else:
            return False

    @staticmethod
    def _quarter_num_to_month(quarter_number):
        """Convert a quarter number in the number of first month."""
        # print quarter_number
        if not quarter_number:
            return None

        replacements = collections.OrderedDict()
        replacements["IV"] = "4"
        replacements["III"] = "3"
        replacements["II"] = "2"
        replacements["I"] = "1"

        # replace strings and convert to int
        if not isinstance(quarter_number, int):
            quarter_number = str(quarter_number)
            for orig, new in replacements.items():
                quarter_number = quarter_number.replace(orig, new)
            quarter_number = int(quarter_number.strip())

        if quarter_number == 1:
            month = 1
        elif quarter_number == 2:
            month = 4
        elif quarter_number == 3:
            month = 7
        else:
            month = 10

        return month


class ParseComposedQuarter1(BaseComposedQuarter, BasePEG):

    """Parse quarterly dates from strings composed by substrings with date
    info of the structure showed in the example.

    >>> orig = ["'1986    1º trim.",
    ...     "'            2º trim.",
    ...     "'            3º trim.",
    ...     "'            4º trim.",
    ...     "'1987        I (1) ",
    ...     "'            II * ",
    ...     "'            III * (2) *",
    ...     "'            IV "]
    >>> params = {}
    >>>
    >>> last = None
    >>> time_parser = ParseComposedQuarter1()
    >>> for str_date in orig:
    ...     new = time_parser.parse_time(params, str_date, last)
    ...     last = new
    ...     print(new)
    1986-01-01T00:00:00+00:00
    1986-04-01T00:00:00+00:00
    1986-07-01T00:00:00+00:00
    1986-10-01T00:00:00+00:00
    1987-01-01T00:00:00+00:00
    1987-04-01T00:00:00+00:00
    1987-07-01T00:00:00+00:00
    1987-10-01T00:00:00+00:00
    """

    @classmethod
    def make_parsley_grammar(cls):
        """Return a parsley parsing expression grammar."""
        return parsley.makeGrammar("""
            not_d_or_q = anything:x ?(x not in "0123456789IV()")
            q_str = ('I' | 'V'):q -> q
            q_int = digit:q ?(q in "1234") -> int(q)
            ref = ws '(' digit{1, 3} ')' ws | '*'
            q_num_or_let = (<q_str{1, 3}> | q_int):q -> q

            quarter = not_d_or_q* q_num_or_let:q not_d_or_q* -> q
            year = not_d_or_q* <digit{4}>:y not_d_or_q* -> int(y)

            date = year?:y quarter:q ref? not_d_or_q* ref? ->(y, q_to_m(q), 1)
            """, {"q_to_m": cls._quarter_num_to_month})


class ParseComposedQuarter2(BasePEG, BaseComposedQuarter):

    """Parse quarterly dates from strings composed by substrings with date
    info of the structure showed in the example.

    >>> orig = ["2° Trim 07",
    ...         "u' 3 Trim 07 2'",
    ...         "4° Trim 07 ",
    ...         "1° Trim 08 "]
    >>> last = None
    >>> time_parser = ParseComposedQuarter2()
    >>> for str_date in orig:
    ...     new = time_parser.parse_time({}, str_date, last)
    ...     last = new
    ...     print(new)
    2007-04-01T00:00:00+00:00
    2007-07-01T00:00:00+00:00
    2007-10-01T00:00:00+00:00
    2008-01-01T00:00:00+00:00
    """

    @classmethod
    def make_parsley_grammar(cls):
        """Return a parsley parsing expression grammar."""
        return parsley.makeGrammar("""
                not_digit = anything:x ?(x not in "0123456789 ")

                q = not_digit* ws digit:q not_digit* ws -> int(q)
                y = (ws | not_digit) <digit{2}>:y (ws | not_digit) -> y
                ref = ws '(' digit{1, 3} ')' ws | '*'

                date = q:q not_digit* y:y ref? ws anything{0, 3} -> (dob_year(y), q_to_m(q), 1)
                """, {"q_to_m": cls._quarter_num_to_month,
                      "dob_year": cls._dob_year_to_four})


class ParseComposedQuarter3(BasePEG, BaseComposedQuarter):

    """Parse quarterly dates from strings composed by substrings with date
    info of the structure showed in the example.

    >>> orig = ["III 01",
    ...         "IV 01",
    ...         "I 02",
    ...         "II 02"]
    >>> last = None
    >>> time_parser = ParseComposedQuarter3()
    >>> for str_date in orig:
    ...     new = time_parser.parse_time({}, str_date, last)
    ...     last = new
    ...     print(new)
    2001-07-01T00:00:00+00:00
    2001-10-01T00:00:00+00:00
    2002-01-01T00:00:00+00:00
    2002-04-01T00:00:00+00:00
    """

    @classmethod
    def make_parsley_grammar(cls):
        """Return a parsley parsing expression grammar."""
        return parsley.makeGrammar("""
                separator = anything:x ?(x in "-/.T ")
                not_digit = anything:x ?(x not in "0123456789-/. ")
                ref = ws '(' digit{1, 3} ')' ws | '*'

                q = <not_digit*>:q -> q
                y = <digit{2}>:y -> y

                date = ws ref? q:q separator* y?:y ref? ws anything{0, 3} -> (dob_year(y), q_to_m(q), 1)
                """, {"q_to_m": cls._quarter_num_to_month,
                      "dob_year": cls._dob_year_to_four})


class ParseComposedYearQuarter1(BasePEG, BaseComposedQuarter):

    """Parse multifrequency YQQQQ time strings like the example below.

    >>> orig = ["2008    Año *",
    ...         "Trimestre    I *",
    ...         "             II * (2)",
    ...         "             III *",
    ...         "             IV *"]
    >>> params = {"time_format": str}
    >>>
    >>> last = None
    >>> time_parser = ParseComposedYearQuarter1()
    >>> for str_date in orig:
    ...     new = time_parser.parse_time(params, str_date, last)
    ...     last = new
    ...     print(new)
    2008-01-01T00:00:00+00:00
    2008-01-01T00:00:00+00:00
    2008-04-01T00:00:00+00:00
    2008-07-01T00:00:00+00:00
    2008-10-01T00:00:00+00:00
    """

    @classmethod
    def _accepts(cls, params, curr_time, last_time=None, next_time=None):
        if not (params["time_composed"] and params["frequency"] == "AQQQQ"):
            return False

        try:
            cls.make_parsley_grammar()(curr_time).date()
            return True
        except:
            return False

    @classmethod
    def make_parsley_grammar(cls):
        """Return a parsley parsing expression grammar."""
        return parsley.makeGrammar("""
            not_digit = anything:x ?(x not in "0123456789")
            not_d_or_q = anything:x ?(x not in "0123456789IV()")
            q_letter = ('I' | 'V'):q -> q
            ref = ws '(' digit{1, 3} ')' ws | '*'

            quarter = not_d_or_q* <q_letter{1, 3}>:q not_d_or_q* -> q
            year = not_digit* <digit{4}>:y not_digit* -> int(y)

            date = year?:y quarter?:q ref? not_d_or_q* ref? ->(y, q_to_m(q), 1)
            """, {"q_to_m": cls._quarter_num_to_month})


class ParseComposedQuarterYear1(ParseComposedYearQuarter1):

    """Parse multifrequency QQQQY time strings like the example below.

    >>> orig = ["2003 I",
    ...         "II",
    ...         "III",
    ...         "IV",
    ...         "Año"]
    >>> params = {"time_format": str}
    >>>
    >>> last = None
    >>> time_parser = ParseComposedQuarterYear1()
    >>> for str_date in orig:
    ...     new = time_parser.parse_time(params, str_date, last)
    ...     last = new
    ...     print(new)
    2003-01-01T00:00:00+00:00
    2003-04-01T00:00:00+00:00
    2003-07-01T00:00:00+00:00
    2003-10-01T00:00:00+00:00
    2003-01-01T00:00:00+00:00
    """

    @classmethod
    def _accepts(cls, params, curr_time, last_time=None, next_time=None):
        if not (params["time_composed"] and params["frequency"] == "QQQQA"):
            return False

        try:
            cls.make_parsley_grammar()(curr_time).date()
            return True
        except:
            return False

    @classmethod
    def _fill_parse_date_holes(cls, result, last_time):
        """Analyze parsed result with last time to complete missings.

        Every missing is replaced with the value of the last time value,
        except if year and month are missing, and the last time value
        represents the 4th quarter of a year. This will be interpreted as the
        "year" part of the QQQQY multifrequency time index.

        Args:
            result (tuple): (year, month, day) Each element could be an integer
                or None.
            last_time (arrow.Arrow): Last time value parsed.

        Returns:
            tuple: (year, month, day) All the elements are integers, providing
                all the information to create a new time value.
        """

        # take new date elements found with the grammar
        if last_time:
            if not result[0] and not result[1] and last_time.month == 10:
                year = int(last_time.year)
                month = 1
            else:
                year = int(result[0] or last_time.year)
                month = int(result[1] or last_time.month)
        else:
            year = int(result[0] or 1)
            month = int(result[1] or 1)

        return year, month, 1


class BaseComposedSemester():

    """Parse dates from strings composed by substrings with date info.
    Only for semester series."""

    @classmethod
    def _accepts(cls, params, curr_time, last_time=None, next_time=None):

        if params["time_composed"] and params["frequency"] == "S":
            try:
                cls.make_parsley_grammar()(curr_time).date()
            except:
                return False
            return True
        else:
            return False

    @staticmethod
    def _semester_num_to_month(semester_number):
        """Convert a semester number in the number of first month."""
        # print quarter_number
        if not semester_number:
            return None

        replacements = collections.OrderedDict()
        replacements["II"] = "2"
        replacements["I"] = "1"

        # replace strings and convert to int
        if not isinstance(semester_number, int):
            semester_number = str(semester_number)
            for orig, new in replacements.items():
                semester_number = semester_number.replace(orig, new)
            semester_number = int(semester_number.strip())

        if semester_number == 1:
            month = 1
        else:
            month = 7

        return month


class ParseComposedSemester(BasePEG, BaseComposedSemester):

    """Parse semester dates from strings composed by substrings with date
    info of the structure showed in the example.

    >>> orig = ["(2)I.S.03",
    ...         "II.S.03*",
    ...         "I.S.04",
    ...         "*II.S.04",
    ...         "I.S.05(1)"]
    >>> last = None
    >>> time_parser = ParseComposedSemester()
    >>> for str_date in orig:
    ...     new = time_parser.parse_time({}, str_date, last)
    ...     last = new
    ...     print(new)
    2003-01-01T00:00:00+00:00
    2003-07-01T00:00:00+00:00
    2004-01-01T00:00:00+00:00
    2004-07-01T00:00:00+00:00
    2005-01-01T00:00:00+00:00
    """

    @classmethod
    def make_parsley_grammar(cls):
        """Return a parsley parsing expression grammar."""
        return parsley.makeGrammar("""
                separator = anything:x ?(x in "-/.S ")
                not_digit = anything:x ?(x not in "0123456789-/. ")
                ref = ws '(' digit{1, 3} ')' ws | '*'

                s = <not_digit*>:s -> s
                y = <digit{2}>:y -> y

                date = ws ref? s:s separator* y?:y ref? ws anything{0, 3} -> (dob_year(y), s_to_m(s), 1)
                """, {"s_to_m": cls._semester_num_to_month,
                      "dob_year": cls._dob_year_to_four})


class BaseComposedMonth():

    """Parse dates from strings composed by substrings with date info.
    Only for quarterly series."""

    @classmethod
    def _accepts(cls, params, curr_time, last_time=None, next_time=None):

        if not (params["time_composed"] and params["frequency"] == "M"):
            return False

        try:
            cls.make_parsley_grammar()(curr_time).date()
            return True
        except:
            return False

    @classmethod
    def _month_str_to_num(cls, month_str):
        """Convert month string in month number.

        >>> BaseComposedMonth._month_str_to_num("ene")
        1
        >>> BaseComposedMonth._month_str_to_num("jan")
        1
        >>> BaseComposedMonth._month_str_to_num("september")
        9
        >>> BaseComposedMonth._month_str_to_num("septiembre")
        9
        """

        loc_iter = (arrow.locales.__dict__[l] for l in vars(arrow.locales)
                    if l[-6:] == "Locale")
        for local in loc_iter:
            month_num = local().month_number(month_str.capitalize())
            if month_num:
                break

        return month_num


class ParseComposedMonth1(BasePEG, BaseComposedMonth):

    """Parse quarterly dates from strings composed by substrings with date
    info of the structure showed in the example.

    >>> orig = ["1991    Ene. ",
    ...         "1991    Febrero",
    ...         "1991    Marzo. (1)",
    ...         "Abril.    1991 (2)",
    ...         "Mayo.  (3)  1991",
    ...         "Jun.        ",
    ...         "Julio.     *  "]
    >>> params = {"time_format": str}
    >>>
    >>> last = None
    >>> time_parser = ParseComposedMonth1()
    >>> for str_date in orig:
    ...     new = time_parser.parse_time(params, str_date, last)
    ...     last = new
    ...     print(new)
    1991-01-01T00:00:00+00:00
    1991-02-01T00:00:00+00:00
    1991-03-01T00:00:00+00:00
    1991-04-01T00:00:00+00:00
    1991-05-01T00:00:00+00:00
    1991-06-01T00:00:00+00:00
    1991-07-01T00:00:00+00:00
    """

    @classmethod
    def make_parsley_grammar(cls):
        """Return a parsley parsing expression grammar."""
        return parsley.makeGrammar("""
                not_digit = anything:x ?(x not in "0123456789 ")
                not_d_or_p = anything:x ?(x not in "0123456789()")
                sep = ws anything:x ws ?(x in ".-/,")

                y = (ws | not_digit) <digit{2, 4}>:y (ws | not_digit) -> y
                m = ws <letter{3, 50}>:m '.'? -> m
                ref = ws '(' digit{1, 3} ')' ws | '*'

                y_m = y:y ref? sep? m:m anything* -> (year(y), month(m), 1)
                m_y = m:m ref? sep? y:y anything* -> (year(y), month(m), 1)
                only_m = m:m anything* -> (None, month(m), 1)

                date = y_m | m_y | only_m
                """, {"month": cls._month_str_to_num,
                      "year": cls._dob_year_to_four})


class ParseComposedMonth2(BasePEG, BaseComposedMonth):

    """Parse quarterly dates from strings composed by substrings with date
    info of the structure showed in the example.

    >>> orig = ["1991,01 ",
    ...         "1991.01 ",
    ...         "1991,02  ",
    ...         "1991.02  ",
    ...         " 03,1991  ",
    ...         "04       ",
    ...         "05       ",
    ...         "06       "]
    >>> params = {"time_format": str}
    >>>
    >>> last = None
    >>> time_parser = ParseComposedMonth2()
    >>> for str_date in orig:
    ...     new = time_parser.parse_time(params, str_date, last)
    ...     last = new
    ...     print(new)
    1991-01-01T00:00:00+00:00
    1991-01-01T00:00:00+00:00
    1991-02-01T00:00:00+00:00
    1991-02-01T00:00:00+00:00
    1991-03-01T00:00:00+00:00
    1991-04-01T00:00:00+00:00
    1991-05-01T00:00:00+00:00
    1991-06-01T00:00:00+00:00
    """

    @classmethod
    def make_parsley_grammar(cls):
        """Return a parsley parsing expression grammar."""
        return parsley.makeGrammar("""
                not_digit = anything:x ?(x not in "0123456789")

                y = (ws | not_digit) <digit{4}>:y (ws | not_digit) -> y
                m = (ws | not_digit) <digit{1, 2}>:m (ws | not_digit) -> int(m)

                y_m = y:y not_digit* m:m anything* -> (y, m, 1)
                m_y = m:m not_digit* y:y anything* -> (y, m, 1)
                only_m = m:m anything* -> (None, m, 1)

                date = y_m | m_y | only_m
                """, {})


class BaseComposedYear():

    """Parse dates from strings composed by substrings with date info.
    Only for yearly series."""

    @classmethod
    def _accepts(cls, params, curr_time, last_time=None, next_time=None):

        if not (params["time_composed"] and params["frequency"] == "A"):
            return False

        try:
            cls.make_parsley_grammar()(curr_time).date()
            return True
        except:
            return False


class ParseComposedYear1(BasePEG, BaseComposedYear):

    """Parse yearly dates from strings composed by substrings with date
    info of the structure showed in the example.

    >>> orig = ["1995    (1)",
    ...         "1996    (2)",
    ...         "1997       ",
    ...         "(3)  1998  ",
    ...         "(4)  1999  "]
    >>> params = {"time_format": str}
    >>>
    >>> last = None
    >>> time_parser = ParseComposedYear1()
    >>> for str_date in orig:
    ...     new = time_parser.parse_time(params, str_date, last)
    ...     last = new
    ...     print(new)
    1995-01-01T00:00:00+00:00
    1996-01-01T00:00:00+00:00
    1997-01-01T00:00:00+00:00
    1998-01-01T00:00:00+00:00
    1999-01-01T00:00:00+00:00
    """

    @classmethod
    def make_parsley_grammar(cls):
        """Return a parsley parsing expression grammar."""
        return parsley.makeGrammar("""
                not_digit = anything:x ?(x not in "0123456789")
                not_d_or_p = anything:x ?(x not in "0123456789()")
                ref = not_d_or_p* '(' digit{1, 3} ')' not_d_or_p*

                year = not_d_or_p* <digit{4}>:y not_d_or_p* -> int(y)

                date = ref? year:y ref? -> (y, 1, 1)
                """, {})


class ParseComposedYear2(BasePEG, BaseComposedYear):

    """Parse yearly dates from agricultural campaings that follow a pattern
    like shown in the example.

    >>> orig = ["1995/96 (1) ",
    ...         "1996/97 (2) ",
    ...         "(3)  1997/98",
    ...         "(4)  1998/99"]
    >>> params = {"time_format": str}
    >>>
    >>> last = None
    >>> time_parser = ParseComposedYear2()
    >>> for str_date in orig:
    ...     new = time_parser.parse_time(params, str_date, last)
    ...     last = new
    ...     print(new)
    1995-01-01T00:00:00+00:00
    1996-01-01T00:00:00+00:00
    1997-01-01T00:00:00+00:00
    1998-01-01T00:00:00+00:00
    """

    @classmethod
    def make_parsley_grammar(cls):
        """Return a parsley parsing expression grammar."""
        return parsley.makeGrammar("""
                not_digit = anything:x ?(x not in "0123456789")
                not_d_or_p = anything:x ?(x not in "0123456789()")
                ref = not_d_or_p* '(' digit{1, 3} ')' not_d_or_p*

                year = <digit{4}>:y'/'<digit{2}> -> int(y)

                date = ref? year:y ref? -> (y, 1, 1)
                """, {})


def get_strategies():
    """Return all the concrete strategies available in this module.

    This method avoid to return base classes and exceptions."""

    return xlseries.utils.strategies_helpers.get_strategies()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    pprint(sorted(xlseries.utils.strategies_helpers.get_strategies_names()))
