from __future__ import print_function

from ib.ext.Contract import Contract
from ib.ext.Order import Order
from ib.opt import Connection


def error_handler(msg):
    """
    A function that prints the error messages from Interactive Brokers
    :param msg: the error message
    :return:
    """
    print("Server Error:", msg)


def server_handler(msg):
    """
    A function that prints the messages from Interactive Brokers
    :param msg: the error message
    :return:
    """
    print("Server Msg:", msg.typeName, "-", msg)

def create_contract(symbol, sec_type, exch, prim_exch, curr):
    """

    :param symbol: symbol of the security
    :param sec_type: security type. Look at Types.java
    :param exch: name of the exchange
    :param prim_exch: name primary exchange
    :param curr: name of the currency
    :return: contract
    """
    contract = Contract()
    contract.m_symbol = symbol
    contract.m_secType = sec_type
    contract.m_exchange = exch
    contract.m_primaryExch = prim_exch
    contract.m_currency = curr
    return contract


def create_order(order_type, quantity, action):
    """

    :param order_type: type of the order e.g. Market or Limit order. Also see OrderType.java
    :param quantity: quantity required
    :param action: buy or sell. See Types.java
    :return: order
    """
    order = Order()
    order.m_orderType = order_type
    order.m_totalQuantity = quantity
    order.m_action = action
    return order


if __name__ == "__main__":
    # The port number has the same value as defined in our API settings of TWS
    port = 7497

    # The client_id variable is our assigned integer that identifies
    # the instance of the client communicating with TWS
    client_id = 1

    # The order_id variable is our assigned integer that identifies
    # the order queue number sent to TWS. Each new order requires
    # this value to be incremented sequentially
    order_id = 122

    tws_conn = None
    try:
        # create a IB connection instance
        tws_conn = Connection.create(port=port, clientId=client_id)
        # make a connection
        tws_conn.connect()
        # register the error handler
        tws_conn.register(error_handler, 'Error')
        # register the server handler
        tws_conn.registerAll(server_handler)
        # create a contract
        aapl_contract = create_contract(
            'AAPL',
            'STK',
            'SMART',
            'SMART',
            'USD'
        )
        # create an oder to long 10 shares of AAPL
        aapl_order = create_order('MKT', 10, 'SELL')
        # finally place the order
        tws_conn.placeOrder(order_id, aapl_contract, aapl_order)
    finally:
        if tws_conn is not None:
            tws_conn.disconnect()
