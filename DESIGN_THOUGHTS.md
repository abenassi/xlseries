
Design thoughts about the package
====

*This is a list of design thoughts that have appeared in building/modifying this package and their provisional resolution. They should be taken as useful indicators of what was the developer maintaining this package thinking when making design decisions.*

* **How extremely similar tests should be written?**. test_xlseries.py has the same kind of test just repeated over and over again.
    - There will be a helper function that take the case number as an argument to the rest of test operations.
* **How to structure the strategies in a hierarchy of levels of abstraction?**. There is more than one level in which strategies operate. The higher level of abstraction delegates many tasks into other subsets of strategies.
    - Current way relies on a hierarchy of folders that make lower level strategies only accessible by the higher level ones that could use them.
* **Trade off between explicit parameters and scope control vs. readability and convenience of passing too many parameters between functions**. What should be the threshold to pass an object instead of several parameters? Should I create more specific objects than Parameters?
    - Let's try to push a bit more the threshold to pass arguments instead of the parameters objects entirely.
* **Check convenience of granularity in clean data methods**. Should they all be already in the main methods? Is it convenient to have them separated?
* **When should something in a strategy be an instance data member or some argument passed to a function?**. OOP vs. functional programming?
    - Passing arguments to a function should be preferred when no status is really needed to be preserved or accessible broadly.
* **What to do with some functions that are shared by different kinds of strategies?**. 
    - For the time being they are "utils" and they have a specific util module regarding they kind of functionality
* **Organizing kinds of test files**. Integration and unit tests is an appropriate way to do this? Is there any other category of tests that could help structure them in a better way?
* **How to wrap different decorators in a single one?**. How convenient is to have multiple decorators upon a test method?
    - Tests will be refactored using a helper function in which decorators functionality is applied once, without needing to repeat it in all the test methods.
* **Structure a package in a hierarchy of folders vs. have just one level of subpackages**
    - Hierarchy of folders shows a structure of the flow of the program itself that is clearer than have same level folders.
* **Compare data-frames should show side by side the things that are being compared**. Just knowing they are different doesn't help a lot to figure out how they are different (raise exceptions when the value doesn't match?).
    - They will just throw an exception in the very moment a difference is detected.
* **Message for custom exceptions should be composed in the code or by the custom exception itself?**. The downside of making the custom exception compose the message is that the interface of it will be different to the one normally expected for python exceptions `def __init__(self, message, errors)` will be something like `def __init__(self, arg1, arg2, arg3, errors)` because the exception will take the args to compose a custom message.
    - Even if the usual python interface for an exception is changed in this way, it eases a lot the use of custom exceptions to be able to just pass the values that the user should look at to understand why an exception was raised instead of having to compose the message everywhere in the code when an exception is put in place.
