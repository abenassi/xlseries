<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Brainstorming some strategies ideas](#brainstorming-some-strategies-ideas)
  - [ParameterDiscovery](#parameterdiscovery)
  - [Parse time](#parse-time)
  - [Parameters: give or discover?](#parameters-give-or-discover)
    - [`alignment`](#alignment)
    - [`headers_coord`](#headers_coord)
    - [`composed_headers`](#composed_headers)
    - [`data_starts`](#data_starts)
    - [`data_ends`](#data_ends)
    - [`continuity` and `blank_rows`](#continuity-and-blank_rows)
    - [`missings` and `missing_value`](#missings-and-missing_value)
    - [`multifrequency` and `frequency`](#multifrequency-and-frequency)
    - [`time_format` and `time_composed` and `time_multicolumn`](#time_format-and-time_composed-and-time_multicolumn)
    - [`time_header_coord`](#time_header_coord)
  - [Meta-data scope of the package](#meta-data-scope-of-the-package)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

Brainstorming some strategies ideas
====

## ParameterDiscovery
This strategy assumes that you can gather a list of input parameters for parsing time data series in an excel file, and that this should be enough to do it right. You may have the parameters or you may have to discover them.

1. Discovering parameters about the excel file
2. Clean input from mistakes and difficult to parse strings before start using the file
3. Using parameters to safely extract the data

## Parse time
Parse time should be able to call strategies that can parse/deal with any kind of composed strings expressing any kind of time frequency, given the parameter of the frequency (or maybe even without that parameter).
    * Parsing expression grammars?
    * Hierarchies of strategies for "parse_time" depending on frequency?

## Parameters: give or discover?
The first approach assumes that the user provides an extensive list of parameters. On a second stage, strategies to discover some of these parameters will be written. 

The idea would be that the package take a Parameters object with none, some or all of the parameters. Then attempts to discover the parameters that are unknown and, eventually, ask the user for the parameters that couldn't be discovered. All the parameters will be listed in the README of the package regarding two aspects:
    1. How critical are those parameters to successfully scrape an excel spreadsheet.
    2. If they can be automatically discovered by the package or the user must necessarily provide them.

*Next, some ideas about how to discover some parameters*
### `alignment`
* Look at the first columns/rows looking for a sequence of values that can be parsed into a date format. The alignment of the date values should be enough to presume the alignment of the data series in the spreadsheet. Next to the time values there should be at least one sequence of float values indicating actual data.

### `headers_coord` 
* Headers coordinates could be discovered just having `data_starts` parameter and looking up to the first string that is not an empty or `None` value. There should be a way to look for new series (consecutive sequences of float values?) to find new headers up to the end of the file (end of spreadsheet dimension or starting only blank cells from the end point).
* If a `series_names` parameter is given, first rows/columns could be searched for strings approximately matching any of the `series_names` provided. Only headers coordinates for names provided would be taken, so this option would act also as a filter to get some of the series but not all.

### `composed_headers`
* From a header coordinate, look up to see if there is a string value right before the header. That should indicate the presence of `composed_headers`. Also a merged cell should be an indicator of composed headers (probably even a stronger indicator of it).

### `data_starts`
* Tag rows with ratio of digits over total characters in the row. When a certain (low) ratio of digits changes towards a high ratio of digits consistently (for more than one row), we should be at the row where data starts.
* Row of first date value in time index could be another way to predict where `data_starts`. 

### `data_ends`
* Tag rows with ratio of digits as done for `data_starts` discovery. When ratio goes significantly up or excel file ends (hit the dimension boundary -as interpreted by `openpyxl`- or blank rows starting from there) there should be the end of data.

### `continuity` and `blank_rows`
* These two parameters should be discovered together. `blank_rows` indicates that a series is interrupted by blank rows from time to time and `continuity` indicates (when `False`) that a series is interrupted by strings that are no blank rows or data (in test_case2.xlsx there is an example in which a series is interrupted by blank rows and by the time values of the time index itself.)

### `missings` and `missing_value`
* Presence of missings can be determined by following a data series values together with the time index values. Whenever a data value is a string that cannot be converted to a float but there is a valid time index value on the same row, we are in the presence of a missing value.
* If the time index values are not contiguous at some point (non consecutive but future time value comes next after another valid time value) we have "Implicit" missing values (because there are holes in the time representation).

### `multifrequency` and `frequency`
* If the time index values are directly parsed into datetime.datetime it wouldn't be difficult to infer the frequency from a sample of the first time values.
* Strategies to infer frequency from more complex string time values should be attached to strategies to discover `time_multicolumn`, `time_alignment`, `time_header_coord` since it's part of the same problem: understand the structure of the time index and gather parameters about it that other strategies can have for granted to operate.

### `time_format` and `time_composed` and `time_multicolumn`
* When looking for date values, if something could be parsed by `openpyxl` directly into `datetime.datetime` the time format is certain. But if strings have to be evaluated, there should be a strategy to identify if a string could be a date (maybe iterating through the existing date parsing strategies asking for `accepts(possible_str_date)`). This would probably have to be figured it out together with `time_composed` (if the string represents a known date format or if it is composed by elements that have to be interpreted to parse a date from them) and `time_multicolumn` that could hold relevant elements to parse a date in more than one column.

### `time_header_coord`
* Time header coordinate could be searched with approximate string matching if `time_header` is provided.
* If time header is not provided, an approximate string matching search could be performed against a dictionary of well-known ways to express the name of a time values index in different languages (like "Date", "Time", "Fecha", "Datum", etc.)
* If no certain time header can be found, the time header would be the cell right above the first time value in a time value index.

## Meta-data scope of the package
* **Progressive aggregation**. When facing hierarchical groups of time data series, there are groups of them that added together conform an aggregated time data series that is also present in the spreadsheet. In these cases, the name of the low-level series should be composed to reflect that they are part of a high-level one (eg. "GDP" can be decomposed into 10 chapters like "Agriculture", "Services", etc. - see test cases 6 and 7 for an example of this). This could be addressed later on the process, as something optional, after the package already extracted successfully all the series with their low-level names. The implementation of this feature though, is a low priority for the moment given its complexity and little value added for the expected user case.
    - Exploring all the possible adding combinations of the first values of the series in order, assuming that aggregated series should immediately follow (or being right before) a group of low-level ones (test case 6) could be a reasonable strategy.
    - Exploring all the possible adding combinations disregarding the order is another possibility, but this would take much more time.
    - Using additional characteristics of the header cells format could be another strategy, but is complicated to generalize enough to make this strategy useful in a variety of cases (test case 7).

