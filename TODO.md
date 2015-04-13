TODO list for xlseries package
====

- [ ] Build test interface to be nicer, specially inside "compare_data_frames" method.
- [ ] Write tests for discovering parameters.
- [ ] Explore the possibility of using a package to color error outputs for testing.
- [ ] Add a high level method in user interface that catches errors raised during the process of parsing an excel file and returns None.
- [ ] Make the errors in parsing an excel files be custom designed Exceptions instead of using status returns.
- [ ] Create docs with Sphinx - read the docs.
- [ ] Create blogspots with how to contribute.
- [ ] Add screenshots of messy excel files in the README.
- [ ] Build command line interface
- [ ] Add installation instructions to the README
- [ ] Describe ways to add a new test case
- [ ] Use os.path to manipulate paths, don't just use a path separator and strings!
- [ ] Cases description could be added __doc__ from CASES.md
- [ ] Integration expected examples should be saved in a more native format than xlsx like CSV or a proper pandas data frame serialization tool
- [ ] Strategies should be call with a domain name problem, not "strategies"
- [ ] Replace tests with helper functions that take out all the decorators and use an argument to know which case number to call.
