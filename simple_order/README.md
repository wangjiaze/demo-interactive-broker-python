# A simple order
This example shows how to long 10 AAPL shares. There are three key aspects:

1. Create a contract
2. Create an order
3. Place an order

## Create a contract
We need to create a contract first before making an order. The contract
contains information about the security, exchange and the currency.
More information about the security type can be found in Types.java.

## Create an oder
In this step we create an order by specifying the order type, quantity
and the action to take. More information about the order type can be found
in OderType.java or in the TWS workstation under the mosaic "Activity".

## Place an order
Once we create the contract and the order, an oder can be placed.
This required a unique `oder_id` set by the user.