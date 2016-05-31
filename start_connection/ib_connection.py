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


if __name__ == "__main__":
    port = 7497
    client_id = 1
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
    finally:
        if tws_conn is not None:
            tws_conn.disconnect()
