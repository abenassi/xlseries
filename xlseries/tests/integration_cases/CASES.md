
Excel file test cases
====

This list of excel file cases is ordered, approximately, by difficulty in its time data series extraction. Each case has notes regarding the particular issues of extracting data series for that file in a differential way with respect to the previous one (only new issues are noted, because they mark new things to deal with).

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Excel file test cases
](../original/)
- [Cases](#cases)
  - [Case 1](#case-1)
  - [Case 2](#case-2)
  - [Case 3](#case-3)
  - [Case 4](#case-4)
  - [Case 5](#case-5)
  - [Case 6](#case-6)
  - [Case 7](#case-7)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Cases

## Case 1

* Vertical series (always)
* Monthly frequency (always - not multi-frequency)
* Data starts in row 2
* Headers: no header for time field, header for data series
* Secondary series and notes in additional columns
* Continuous main series layout
* Missings in secondary series
* Time-stamp in date format
* Footnotes with source

## Case 2

* Daily frequency (always - not multi-frequency)
* Data doesn't start in row 2
* Headers for data and time field
* Secondary interrupted series (monthly)
* No footnotes
* Time-stamp mistakes: need to clean data before using it

## Case 3

* Quarterly frequency (always - not multi-frequency)
* No secondary series
* Time-stamp in string format. String composed in the same cell.
* Footnotes with source

## Case 4

* Composed name with hierarchy and aggregation of same hierarchy levels
* Missings with strings
* Aggregation data close to the series
* New data series starting after previous ones

## Case 5

* Interrupted layout of data series
* Composed time-stamp using more than one cell
* Time-stamp header far from data starting
* Dirty cells between headers and data start
* False series (meta-data for other series)

## Case 6

* Horizontal series (always)
    - Position of header and footer changes! (is not only a matter of transposing the entire sheet)
* Composed time-stamp plus two frequencies (aggregation in between)
* Different levels of aggregation mixed
* Composed series names at the same hierarchy level (column with a "Total" in the end of several partial columns)
* Progressive aggregation of series identifiable with sum of results, change in capitalization and bold letters

## Case 7

* Progressive aggregation identifiable with strings indentation
