Design thoughts about the package
====

*This is a list of design thoughts that have appeared in building/modifying this package and their provisional resolution. They should be taken as useful indicators of what was the developer maintaining this package thinking when making design decisions.*

* **How extremely similar tests should be written?**. test_xlseries.py has the same kind of test just repeated over and over again.
* **How to structure the strategies in a hierarchy of levels of abstraction?**. There is more than one level in which strategies operate. The higher level of abstraction delegates many tasks into other subsets of strategies.