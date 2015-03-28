===============================
Excel Time Series Scraper
===============================

Python package to scrape time data series from excel files.

# Development status

This package is still in an early development stage, it can't be reliably used for the moment. The design may still be object of radical changes.

## Test cases

There are [7 test cases](https://github.com/abenassi/xlseries/tree/master/tests/integration_cases) ordered in increasing difficulty. All the features of the package are being implemented step by step aiming to handle the next test case in the most general and flexible possible way.

## Progress

Up to this moment the package can handle cases 1 and 2 with parameters. Once the seven cases can be handled with given parameters for each case, strategies for discovering parameters will start to be implemented.

The ultimate goal would be that for **any** given excel file the user can obtain pandas data frames with all the time data series available doing no more than this:

'''python
from xlseries import XlSeries
series = XlSeries("xl_file_name")
dfs = series.get_data_frames()
'''

An intermediate step will be that the user can write a json file with some parameters of the excel file and the data series:

'''python
from xlseries import XlSeries
series = XlSeries("xl_file_name", "json_parameters_file_name")
dfs = series.get_data_frames()
'''

# Problem context (or why this package is a good idea)

Researchers, students, consultants and civil activists that use public data waste a lot of time finding, downloading, understanding, parsing, transforming, comparing, structuring and ultimately updating the data they need to use in their analysis. The process is so time/effort consuming sometimes that can diminish notoriously the capacity of a team or an individual of doing the actual job with the data. Valuable data is not used, avoidable errors are made, duplicity of work is done everywhere, history of data is very often lost, similar data is not compared and ultimate analysis is done with less time, patience and resources than could and should be done.

A package like this one, would be an invaluable tool for automating the process of using data published only in human-readable excel layouts.

## International organisms

There are many public organisms (generally, international organisms) that do a huge work in this field gathering and centralizing data from many countries, but very often this sources are not enough for researchers of third-world countries due to a number of problems:

1. Third-world countries data is frequently scarce, incomplete or doubtful in those big data collector organisms. These are better sources for first-world countries data.
2. International organisms do not use lots of valuable data coming from non official sources that are key to researchers.
3. International organisms make decisions about the data to present a final time-series piece, but lots of comparisons, analysis and research-specific considerations can not be made if only one version of a data series is provided.
4. International organisms have a specific target or framework for its data collection activity that sometimes aims to force cross country comparability or targets certain kinds of data.

Some of the best institutions that collect and organize data are:

* [FRED (Federal Reserve Economic Data)](http://research.stlouisfed.org/fred2/): Excel Add-In, website search, entire database downloadable.
* [World Bank](http://data.worldbank.org/): API, python library, stata library, website search, entire database downloadable.
* [OECD](http://stats.oecd.org/): API, webiste search.

## Some common problems using data in third world-countries (and in others too!)

* Normally, data is available in excel format. There is no structured APIs to access data programatically.
* Excel layouts are very different, even in a single source, and frequently complicated to parse.
* Similar data series across different public offices show different numbers.
* Data is shown in one or more fixed transformations, there is no tool to acquire data with a chosen transformation.
* Data change significantly over time due to re-estimations, there is no track of these changes. Once they are done, original data is lost or complicated to recover and use.
* Updating previously used data with new values requires download and process data again almost duplicating previous work.
* Data series may have several mistakes sometimes. Methodological notes are not always very clarifying and there is no interactive way to share concerns about data with the community that uses it.
* Data is sometimes really hidden. There is no easy or centralized way of searching quickly through the entire corpus of existent public data.






