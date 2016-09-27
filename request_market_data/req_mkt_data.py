from __future__ import print_function

from ib.ext.Contract import Contract
from ib.opt import Connection, message
import datetime as dt
import time


class ReqData:
    def __init__(self):
        self.port = 7497
        self.client_id = 1
        self.order_id = 1
        self.account_code = 'DU434966'
        # self.account_code = 'U1808793'
        self.symbol = 'AAPL'
        self.symbol_id = 0
        self.tick_counter = 0
        self.max_ticks = 20
        self.tws_conn = None
        self.unrealized_pnl = 0
        self.realized_pnl = 0
        self.position = 0
        self.wait_for_message = True

    @staticmethod
    def error_handler(self,msg):
        """
        A function that prints the error messages from Interactive Brokers
        :param msg: the error message
        :return:
        """
        print("-> Server Error:", msg)

    def server_handler(self, msg):
        """
        A function that prints the messages from Interactive Brokers
        :param msg: the error message
        :return:
        """
        print("-> Server Msg:", msg.typeName, "-", msg)

        if msg.typeName == "nextValidId":
            self.order_id = msg.orderId
        elif msg.typeName == "managedAccounts":
            self.account_code = msg.accountsList
        elif msg.typeName == "updatePortfolio" and msg.contract.m_symbol == self.symbol:
            self.unrealized_pnl = msg.unrealizedPNL
            self.realized_pnl = msg.realizedPNL
            self.position = msg.position
        elif msg.typeName == "error" and msg.id != -1:
            return

    def tick_event(self,msg):
        """
        A function that registers the tick events
        :param msg:
        :return:
        """
        # https://www.interactivebrokers.co.uk/en/software/api/apiguide/java/tickprice.htm
        # https://www.interactivebrokers.co.uk/en/software/api/apiguide/java/ticksize.htm

        # print("\ntick_counter = ", self.tick_counter, " time = ", dt.datetime.now())
        # print("msg =  ",msg)

        if self.tick_counter > self.max_ticks :
            # raise Exception('Maximum number of ticks reached')
            print("Cancelling market data updates")
            self.wait_for_message = False
        self.tick_counter += 1

    @staticmethod
    def create_contract(self,symbol, sec_type, exch, prim_exch, curr):
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

    def stat_req_data(self):
        self.tws_conn = None
        try:
            # create a IB connection instance
            self.tws_conn = Connection.create(port=self.port, clientId=self.client_id)
            # make a connection
            self.tws_conn.connect()
            # register the error handler
            self.tws_conn.register(self.error_handler, 'Error')
            # register the server handler
            self.tws_conn.registerAll(self.server_handler)
            # register market data events.
            self.tws_conn.register(self.tick_event, message.tickPrice, message.tickSize)
            # create a contract
            stk_contract = self.create_contract(
                self,
                self.symbol,
                'STK',
                'SMART',
                'SMART',
                'USD'
            )
            # generic_tick_keys = '100,101,104,106,165,221,225,236'
            # request market data
            print("request market data")
            self.tws_conn.reqMktData(self.symbol_id, stk_contract, '236', False)
            # TODO: WITH THIS REQUEST IS RELATIVELY EASY TO COLLECT INFO 46 (SHORTABLE INDEX)
            # TODO: AND 49 (HALTED) THAT CAN BE USED TO DECIDE IF TO GO AHEAD WITH THE TRADE OR NOT
            # TODO: IMPLEMENT THESE TWO DIRECTLY, WITHOUT TRYING TO USE MEDICI'S CONTRACTS
            # TODO: (DEVELOPED FOR A DIFFERENT REASON)

            time.sleep(1)
            print("request account updates")
            # self.tws_conn.reqAccountUpdates(True, self.account_code)

            while self.wait_for_message:
                time.sleep(1)

        except Exception as e:
            print("Error:", e)
            self.wait_for_message = False
            self.tws_conn.cancelMktData(self.symbol)
            time.sleep(1)

        print("disconnecting the machinery")
        if self.tws_conn is not None:
            self.tws_conn.disconnect()


if __name__ == "__main__":
    rd = ReqData()
    rd.stat_req_data()
