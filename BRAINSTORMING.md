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

The idea would be that the package take a Parameters object with none, some or all of the parameters. Then attempts to discover the parameters that are unknown and, eventually, ask the user for the parameters that couldn't be discovered.

*Next, some ideas about how to discover some parameters*
### `alignment`
Look at the first columns/rows looking for a sequence of values that can be parsed into a date 


## Meta-data scope of the package
