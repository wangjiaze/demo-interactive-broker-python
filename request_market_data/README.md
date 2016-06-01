# Request market data
In this example we explain the method of requesting market data from IB.
This is achieved by using `reqMktData` and `reqAccountUpdates` functions.
We also make use of `message.tickPrice` and  `message.tickSize` to
retrieve data from IB. Every time the data is changed these messages
are sent.