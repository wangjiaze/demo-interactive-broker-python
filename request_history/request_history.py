from __future__ import print_function

from ib.ext.Contract import Contract
from ib.opt import Connection, message
import datetime as dt
import time
import pandas as pd

class ReqData:
    def __init__(self):
        self.port = 7497
        self.client_id = 1
        self.order_id = 1
        self.account_code = None
        self.symbol = 'FB'
        self.symbol_id = 0
        self.tick_counter = 0
        self.max_ticks = 20
        self.tws_conn = None
        self.unrealized_pnl = 0
        self.realized_pnl = 0
        self.position = 0
        self.wait_for_message = True
        self.prices = pd.DataFrame(columns=[self.symbol])
        self.is_storing_data = True

        self.DATE_TIME_FORMAT = "%Y%m%d %H:%M:%S"
        self.DURATION_1_HR = '3600 S'
        self.BAR_SIZE_5_SEC = '5 secs'
        self.BAR_SIZE_1_MIN = '1 min'
        self.WHAT_TO_SHOW_TRADES = "TRADES"
        self.RTH_ALL = 0
        self.DATEFORMAT_STRING = 1
        self.GENERIC_TICKS_NONE = ''
        self.SNAPSHOT_NONE = False
        self.MSG_TYPE_HISTORICAL_DATA = "historicalData"

    @staticmethod
    def error_handler(self,msg):
        """
        A function that prints the error messages from Interactive Brokers
        :param msg: the error message
        :return:
        """
        print("-> Server Error:", msg)

    def server_handler(self,msg):
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
        elif msg.typeName == self.MSG_TYPE_HISTORICAL_DATA:
            # store historical data
            # https://www.interactivebrokers.co.uk/en/software/api/apiguide/java/historicaldata.htm

            if msg.WAP == -1:
                self.is_storing_data = False
            else:
                self.is_storing_data = True
                timestamp = dt.datetime.strptime(msg.date, self.DATE_TIME_FORMAT)
                price = msg.close
                self.prices.loc[timestamp, self.symbol] = float(price)
                self.prices = self.prices.fillna(method='ffill')
                self.prices.sort_index(inplace=True)

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

        print("->tick_counter = ", self.tick_counter, " time = ", dt.datetime.now())
        # print("msg =  ",msg)
        # if self.tick_counter > self.max_ticks :
        #     # raise Exception('Maximum number of ticks reached')
        #     print("Cancelling market data updates")
        #     self.wait_for_message = False
        # self.tick_counter += 1

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
            # request market data
            self.tws_conn.reqMktData(
                self.symbol_id,
                stk_contract,
                self.GENERIC_TICKS_NONE,
                self.SNAPSHOT_NONE
            )
            time.sleep(1)
            self.tws_conn.reqAccountUpdates(
                True,
                self.account_code
            )
            # request historical data
            # https://www.interactivebrokers.co.uk/en/software/api/apiguide/java/reqhistoricaldata.htm
            self.tws_conn.reqHistoricalData(
                self.symbol_id,
                stk_contract,
                time.strftime(self.DATE_TIME_FORMAT),
                self.DURATION_1_HR,
                self.BAR_SIZE_1_MIN,
                self.WHAT_TO_SHOW_TRADES,
                self.RTH_ALL,
                self.DATEFORMAT_STRING
            )
            time.sleep(1)

            while self.is_storing_data :
                time.sleep(1)

        except Exception as e:
            print("Error:", e)
            self.wait_for_message = False
            self.tws_conn.cancelMktData(self.symbol)
            time.sleep(1)

        print(self.prices.head())
        print(self.prices.tail())
        print("disconnecting the machinery")
        if self.tws_conn is not None:
            self.tws_conn.disconnect()


if __name__ == "__main__":
    rd = ReqData()
    rd.stat_req_data()