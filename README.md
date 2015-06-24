
xlseries
===============================

[![Coverage Status](https://coveralls.io/repos/abenassi/xlseries/badge.svg?branch=master)](https://coveralls.io/r/abenassi/xlseries?branch=master)
[![Build Status](https://travis-ci.org/abenassi/xlseries.svg?branch=master)](https://travis-ci.org/abenassi/xlseries)

A python package to scrape [time series](https://en.wikipedia.org/wiki/Time_series) from *any* excel file. Like these ones:

![](https://raw.githubusercontent.com/abenassi/xlseries/master/docs/xl_screenshots/test_cases.gif)

And return them turned into [pandas](http://pandas.pydata.org/pandas-docs/dev/index.html) [data frames](http://pandas.pydata.org/pandas-docs/dev/generated/pandas.DataFrame.html).

## Installation

This package is still in an early development stage, it can't be reliably used for the moment and the design may still be object of radical changes. Anyway, if you want to give it a try or [contribute](#contributions) follow these instructions to install it on your machine.

**If you are using Anaconda as your python distribution**

1. `conda create -n xlseries python=2` *Create new environment*
2. `cd project_directory`
3. `source activate xlseries` *Activate the environment*
4. `pip install -e .` *Install the package in developer mode*
5. `pip install -r requirements.txt` *Install dependencies*
6. `deactivate` *Deactivate when you are done*

**If you are using a standard python installation**

1. `cd project_directory`
2. `virtualenv venv` *Create new environment*
3. `source venv/bin/activate` *Activate the environment*
4. `pip install -r requirements.txt` *Install dependencies*
5. `deactivate` *Deactivate when you are done*

## Quick start

```python
from xlseries import XlSeries
series = XlSeries("path_to_excel_file")
dfs = series.get_data_frames("path_to_json_parameters")
```

With the test case number 1:
```python
from xlseries import XlSeries
from xlseries.utils.path_finders import get_orig_cases_path, get_param_cases_path
series = XlSeries(get_orig_cases_path(1))
dfs = series.get_data_frames(get_param_cases_path(1))
```

* **Excel file**: Up to this development point, the excel file must have only one spreadsheet (anyway, only the active one will be used by `xlseries`) and should not be more *complicated* than the [7 test cases](#test-cases):

![](https://raw.githubusercontent.com/abenassi/xlseries/master/docs/xl_screenshots/test_case_1_2_3.png)
![](https://raw.githubusercontent.com/abenassi/xlseries/master/docs/xl_screenshots/test_case_4_5.png)

* **Json parameters**: A full JSON file or python dictionary with parameters must be provided. In future development stages more and more [parameters](#parameters) will be discovered by the package and the user will not need to provide them but as a way to increase the speed.

To give it a try, you can use this [ipython notebook template](docs/notebooks/Example use case.ipynb). If you want to see the test cases that are passing all the tests and get an idea of how far is going `xlseries` at the moment, check out this [ipython notebook with test cases](docs/notebooks/Test cases.ipynb).

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Problem context (*or why this package is a good idea*)](#problem-context-or-why-this-package-is-a-good-idea)
  - [International organisms](#international-organisms)
  - [Some common problems using data in third world-countries (and in others too!)](#some-common-problems-using-data-in-third-world-countries-and-in-others-too)
- [Parameters](#parameters)
- [Development status](#development-status)
  - [Test cases](#test-cases)
  - [Progress](#progress)
- [Contributions](#contributions)
- [Brainstorming and design thoughts about the package](#brainstorming-and-design-thoughts-about-the-package)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Problem context (*or why this package is a good idea*)

Researchers, students, consultants and civil activists that use public data waste a lot of time finding, downloading, understanding, parsing, transforming, comparing, structuring and ultimately updating the data they need to use in their analysis. The process is so time/effort consuming sometimes that can diminish notoriously the capacity of a team or an individual of doing the actual job with the data. Valuable data is not used, avoidable errors are made, duplicity of work is done everywhere, history of data is very often lost, similar data is not compared and ultimate analysis is done with less time, patience and resources than could and should be done.

A package like this one, would be an invaluable tool for automating the process of using data published only in human-readable excel layouts.

### International organisms

There are many public organisms (generally, international organisms) that do a huge work in this field gathering and centralizing time series from many countries, but very often this sources are not good enough for researchers working in third-world country problematics due to a number of problems:

1. Third-world countries data is frequently scarce, incomplete or doubtful in those big data collector organisms. These are better sources for first-world countries data.
2. International organisms do not use lots of valuable data coming from non official sources that are key to researchers.
3. International organisms make decisions about the data to present a final time-series piece, but lots of comparisons, analysis and research-specific considerations can not be made if only one version of a data series is provided.
4. International organisms have a specific target or framework for its data collection activity that sometimes aims to force cross country comparability or targets certain kinds of data.

Some of the best institutions that collect and organize data are:

* [FRED (Federal Reserve Economic Data)](http://research.stlouisfed.org/fred2/): Excel Add-In, website search, entire database downloadable.
* [World Bank](http://data.worldbank.org/): API, python library, stata library, website search, entire database downloadable.
* [OECD](http://stats.oecd.org/): API, webiste search.

### Some common problems using data in third world-countries (and in others too!)

* Normally, data is available in excel format. There is no structured APIs to access data programatically.
* Excel layouts can be very different, even within a single source, and frequently complicated to parse.
* Similar time series across different public offices show different numbers.
* Data is shown in one or more fixed transformations, there is no tool to acquire data with a chosen transformation.
* Data change significantly over time due to re-estimations, there is no track of these changes. Once they are done, original data is lost or complicated to recover and use.
* Updating previously used data with new values requires download and process data again almost duplicating previous work.
* Data series may have several mistakes sometimes. Methodological notes are not always very clarifying and there is no interactive way to share concerns about data with the community that uses it.
* Data is sometimes really hidden. There is no easy or centralized way of searching quickly through the entire corpus of existent public data.

## Parameters

Each time series has it's own parameters. Parameters can be passed to `XlSeries.get_data_frames()` as a path to a json file that looks like this: 

*Parameters for [test case 2](../tests/intergration_cases/parameters/test_case2.json)*
```json
{"alignment": "vertical",
 "blank_rows": [false, true],
 "data_starts": [5, 22],
 "data_ends": [2993, 2986],
 "frequency": ["D", "M"],
 "headers_coord": ["D4", "F4"],
 "continuity": [true, false],
 "missings": [true, false],
 "missing_value": ["Implicit", null],
 "series_names": null,
 "time_composed": false,
 "time_alignment": [0, -1],
 "time_multicolumn": false,
 "time_header_coord": ["C4", "F4"]}
```

If many series are to be scraped from a single excel file, parameters for each series should be written in lists, but *only if they differ* between series (as you can see in the previous example). It is not necessary to write parameters that repeat themselves in all the series (like the **alignment**, which is usually common to all the series in the spreadsheet).

This list of parameters can still change any time, adding, removing or modifying some of them when the understanding of the problem grows.

*List of parameters*

*Parameters without quotes are non-string values in the **json_way (python_way)***

* **alignment**: "Vertical", "Horizontal" - *Alignment of the series in the spreadsheet.*
* **series_names**: "Real GDP" - *Names of the series (this is not necessary if headers_coord is provided).*
* **headers_coord**: "B4" - *Excel coordinates for a series header.*
* **data_starts**: 4 - *The index of row or column where data starts.*
* **data_ends**: 254 - *The index of row or column where data ends.*
* **continuity**: true (True), false (False) - *Indicates if a data series is interrupted by strings that are not data.*
* **blank_rows**: true (True), false (False) - *Indicates if a data series is interrupted by blank rows.*
* **missings**: true (True), false (False) - *Indicates the presence of missing values in data.*
* **missing_value**: "", ".", "NA", null (None), "Implicit" - *State the value that should be taken as "missing". "Implicit" is a special missing value that means that there are missing values not showed in the spreadsheet (time index is not continuous, typically in day frequency when weekends are not taken into account).*
* **time_alignment**: 0, -1, +1 - *0: Time index run parallel to data, -1: Time value is right before data value cell, +1: Time value is right after data value cell.*
* **time_multicolumn**: true (True), false (False) - *Indicates if a data series has a time index expressed in multiple columns that must be composed.*
* **time_header_coord**: "A3" - *Excel coordinates for a time index header.*
* **time_composed**: true (True), false (False) - *Indicates if a data series has a time index that has to be composed (not a straight forward date string) because some information about current date is taken from previous cells. Typically when year is only stated a the first quarter while the other three have only the quarter number.*
* **frequency**: "Y", "Q", "M", "W", "D" or "YQQQ" and other multi-frequency patterns - *Indicates the time frequency of the series. It uses pretty much the same strings as `datetime.datetime` uses with the substantial aggregation of multi-frequency patterns, when a series has values in more than one frequency at the same row (typically a secondary series is the aggregated version of the other one).*

## Development status

### Test cases

There are [7 test cases](https://github.com/abenassi/xlseries/tree/master/tests/integration_cases). Each test case was chosen because it adds something new that `xlseries` isn't (or wasn't) able to deal with before. Next there is a list of new issues brought by each case, in addition to the previous ones.

#### Test case 1 

<div align="middle">
<img src="https://raw.githubusercontent.com/abenassi/xlseries/master/docs/xl_screenshots/test_case1_c.png"  height="200px">
</div>
* Vertical series (always)
* Monthly frequency (always - not multi-frequency)
* Data starts in row 2
* Headers: no header for time field, header for data series
* Secondary series and notes in additional columns
* Continuous main series layout
* Missings in secondary series
* Time-stamp in date format
* Footnotes with source

#### Test case 2
<div align="middle">
<img src="https://raw.githubusercontent.com/abenassi/xlseries/master/docs/xl_screenshots/test_case2_a.png" height="200px">
</div>
* Daily frequency (always - not multi-frequency)
* Data doesn't start in row 2
* Headers for data and time field
* Secondary interrupted series (monthly)
* No footnotes
* Time-stamp mistakes: need to clean data before using it

<div align="middle">
<img src="https://raw.githubusercontent.com/abenassi/xlseries/master/docs/xl_screenshots/test_case2_bc.png" height="200px">
</div>

*Change from date format to string format (excel types) unexpectedly (left)*
*Human typo in the month of "06-05-11" that should be "06-07-11" (right)*
   

#### Test case 3
<div align="middle">
<img src="https://raw.githubusercontent.com/abenassi/xlseries/master/docs/xl_screenshots/test_case3_a.png" height="200px">
</div>
* Quarterly frequency (always - not multi-frequency)
* No secondary series
* Time-stamp in string format. String composed in the same cell.
* Footnotes with source
      
      
      

#### Test case 4
<div align="middle">
<img src="https://raw.githubusercontent.com/abenassi/xlseries/master/docs/xl_screenshots/test_case4_b.png" height="200px">
</div>
* Composed name with hierarchy and aggregation of same hierarchy levels
* Missings with strings
* Aggregation data close to the series
* New data series starting after previous ones
      

#### Test case 5
<div align="middle">
<img src="https://raw.githubusercontent.com/abenassi/xlseries/master/docs/xl_screenshots/test_case5_a.png" height="200px">
</div>
* Interrupted layout of data series
* Composed time-stamp using more than one cell
* Time-stamp header far from data starting
* Dirty cells between headers and data start
* False series (meta-data for other series)
      
      
      

#### Test case 6
<div align="middle">
<img src="https://raw.githubusercontent.com/abenassi/xlseries/master/docs/xl_screenshots/test_case6_a.png" height="200px">
</div>
* Horizontal series (always)
    - Position of header and footer changes! (is not only a matter of transposing the entire sheet)
* Composed time-stamp plus two frequencies (aggregation in between)
* Different levels of aggregation mixed
* Composed series names at the same hierarchy level (column with a "Total" in the end of several partial columns)
* Progressive aggregation of series identifiable with sum of results, change in capitalization and bold letters
      

#### Test case 7
<div align="middle">
<img src="https://raw.githubusercontent.com/abenassi/xlseries/master/docs/xl_screenshots/test_case7_a.png" height="200px">
</div>
* Progressive aggregation identifiable with strings indentation
      
      
      

### Progress

Up to this moment the package can handle cases [1](#test-case-1), [2](#test-case-2), [3](#test-case-3), [4](#test-case-4) or [5](#test-case-5) with parameters. Once the seven cases can be handled with given parameters for each case, strategies for discovering parameters will start to be implemented.

The ultimate goal is that for **any** given excel file the user can possibly have, `xlseries` be able to extract all time series in the spreadsheet and return pandas data frames.

## Contributions

All contributions are very welcome!

I aim to keep the design of this package strongly modularized and decoupled to allow working in different parts of the problem in an isolated way with respect of other parts of the system.

A non-exhaustive list of ways that you can contribute:

* Bring more test cases that posses parsing challenges not covered by the current test cases. You can add a test case following the example of the other test cases. These can be *integration test cases* (an entire excel worksheet taken from the real world) or *unit test cases* like a new type of time string to parse that is not covered by current time-like strings used as test cases.

* Work in the [parse_time strategies](https://github.com/abenassi/xlseries/blob/master/xlseries/strategies/clean/parse_time.py). These strategies are the most important part of how time indexes are parsed into something that has a datetime.datetime type. You can add more parsers to cover existing cases, improve the ones that already exist giving them more generality or adding new test cases to then implement the parser strategies for them.

* Start building strategies to [clean](https://github.com/abenassi/xlseries/tree/master/xlseries/strategies/clean) values before processing them.

* Start building meta-heuristics to (1) evaluate and compare alternative outputs for the same spreadsheet (pandas data frames) and ranking them by *quality* and (2) build evaluators to determine if a pandas data frame is to be considered a well scraped time data series or not.

* Start working in the still virgin area of *discovering the parameters*. The package still need a list of [parameters](https://github.com/abenassi/xlseries/blob/master/xlseries/strategies/discover/parameters.py) to process the excel files. Many approaches will have to be researched to start building strategies for discovering the parameters of an excel file with time data series:
    - Every parameter has a new module with a bunch of possible strategies to discover it.
    - Machine learning that takes low level input parameters (size of sheet, types of cell values, cell values formatting, etc.) and output the discovered higher level parameter.
    - Trying random parameters and examining the output of the package as a way to discover the correct parameter.

* Start writing the docs.

* Propose different high level designs / rework modules to decouple steps of the algorithms used or to modularize better parts of the system.

**Code style conventions**

For all contributions, we intend to follow the [Google Ptyhon Style Guide](https://google-styleguide.googlecode.com/svn/trunk/pyguide.html)

## Brainstorming and design thoughts about the package

Proximately these two files will be moved to issues, to encourage the participation of other people! You can check out some [design thoughts](../DESIGN_THOUGHTS.md) to look into some decisions that were made (and some decisions that are still being evaluated) and some [brainstorming ideas](../BRAINSTORMING.md) about possible strategies to discover parameters and other stuff like that.






