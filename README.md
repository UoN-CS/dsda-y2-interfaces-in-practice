# Using an interface in team coding

Adam and I have decided to work on a piece of code together.  We want to build a simple system which draws a graph of some electricity consumption data.  We're going to divide the task into two whereby one of us builds the client that draws the graph, and the other loads the data from a source and provides the client a means to access that data.

We started with a whiteboard design session to agree the design of the interface class we would be using.  This establishes a contract that each of has to work to.

![This is an image](whiteboard.jpg)

The client which draws the graph will call methods on an implementation of a ConsumptionData abstract class.  An abstract class is one which contains the concepts (i.e. the method) to be called, but doesn't actually implement them.

Later on we can implement concrete implementation classes.  The two examples on the screenshot above are `ConsumptionDataFile` and `ConsumptionDataDB`.  They should both exhibit the same behaviour to the client, but internally they will store / load the data in a different way.

There is a get_usage_for_range method which returns an integer containing the number of Watt hours (Wh) consumed during the specified range.  The dates are represented by unix timestamps.

We've agreed to use an Exception when the `get_usage_for_range` method cannot return valid data because:

* There is incomplete data for the input range (i.e. data is not available)
* The input range is invalid, e.g. the start date is after the end date.

The client can pro-actively check that it is providing valid data using the `has_usage_for_range` method which returns `True` or `False`