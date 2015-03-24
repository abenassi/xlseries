Brainstorming about high level strategies
====

**ParameterDiscovery**

This strategy assumes that you can gather a list of input parameters for parsing time data series in an excel file, and that this should be enough to do it right. You may have the parameters or you may have to discover them.

1. Discovering parameters about the excel file
2. Clean input from mistakes and difficult to parse strings before start using the file
3. Using parameters to safely extract the data

**Parse time**

Parse time should be able to call strategies that can parse/deal with any kind of composed strings expressing any kind of time frequency, given the parameter of the frequency (or maybe even without that parameter).
    * Parsing expression grammars?
    * Hierarchies of strategies for "parse_time" depending on frequency?
