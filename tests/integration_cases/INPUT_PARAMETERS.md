
Excel file input parameters
====

Characteristics of the excel files that must be taken into account when build the strategies to deal with the input file and that could be parametrized.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Excel file input parameters
](#excel-file-input-parameters)
  - [Basic ones](#basic-ones)
    - [General](#general)
    - [Series name](#series-name)
    - [Data](#data)
    - [Time-stamp](#time-stamp)
  - [Possibly useful ones](#possibly-useful-ones)
  - [More indirect possible parameters](#more-indirect-possible-parameters)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Basic ones

### General
* Series alignment

### Series name
* Simple or composed string name
    - Hierarchical levels
    - Aggregation of same hierarchy levels
    - Both
* Coordinate of the header

### Data
* Row or col data start
    - Right before headers
    - Blank rows in between
    - Dirty rows in between
* Row or col data end
    - Clean end of data (blank rows)
    - Aggregation data right at the end of series
    - New data series starting at the end of previous ones
* Continuous or interrupted series layout
    - Blank rows
    - Different level of aggregations in between
* Existence of missings
* Type of missings
    - Format (string, empty)
    - Explicit or implicit (marked by jumps in time-stamp)
    - Different strings for the same missing
    - Difference between zeros and missings
* False series (they are other series meta-data)
* Series progressive aggregation (accumulating results)

### Time-stamp
* Existence of header for time-stamp
    - Close to data starting
    - Far from data starting
* Simple or composed time-stamp
    - Using more than one cell
    - Using string composing in the same cell
* Row or col of the time-stamp
* Time frequency
    - One frequency
    - More than one frequency in between


## Possibly useful ones
* Type of the time-stamp
* Type of data values
* Presence of footnotes or headernotes
* Multiple or single sheets
* Bold headers and/or data
* Change in string capitalization
* Changes in indentation to detect aggregation of series


## More indirect possible parameters
* Background color of header cells
* Dimension of the excel file (num rows, num cols)
