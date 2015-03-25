Design thoughts about the package
====

*This is a list of design thoughts that have appeared in building/modifying this package and their provisional resolution. They should be taken as useful indicators of what was the developer maintaining this package thinking when making design decisions.*

* **How extremely similar tests should be written?**. test_xlseries.py has the same kind of test just repeated over and over again.
* **How to structure the strategies in a hierarchy of levels of abstraction?**. There is more than one level in which strategies operate. The higher level of abstraction delegates many tasks into other subsets of strategies.
* **Trade off between explicit parameters and scope control vs. readability and convenience of passing too many parameters between functions**. What should be the threshold to pass an object instead of several parameters? Should I create more specific objects than Parameters?
* **Check convenience of granularity in clean data methods**. Should they all be already in the main methods? Is it convenient to have them separated?
* **When should something in a strategy be an instance data member or some argument passed to a function?**. OOP vs. functional programming?
* **What to do with some functions that are shared by different kinds of strategies?**. Provisionally, I have put some time related functions encapsulated as time_utils
* **Should this file be in docs?**. Is this a "doc"?
* **Organizing kinds of test files**. Integration and unit tests is an appropriate for this?
* **How to wrap different decorators in a single one?**. How convenient is to have multiple decorators upon a test method?