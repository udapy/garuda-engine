# execution.py
import os
from loguru import logger
from abc import ABC, abstractmethod

class ExecutionEngine(ABC):
    @abstractmethod
    async def initialize(self):
        pass

    @abstractmethod
    def place_order(self, symbol, transaction_type, quantity=1):
        pass

class ZerodhaEngine(ExecutionEngine):
    def __init__(self):
        self.api_key = os.getenv("ZERODHA_API_KEY")
        self.api_secret = os.getenv("ZERODHA_API_SECRET")
        self.access_token = os.getenv("ZERODHA_ACCESS_TOKEN") # Often generated daily
        self.kite = None
    
    async def initialize(self):
        try:
            from kiteconnect import KiteConnect
            self.kite = KiteConnect(api_key=self.api_key)
            if self.access_token:
                self.kite.set_access_token(self.access_token)
                logger.info("Zerodha Engine Initialized (Token Set)")
            else:
                logger.warning("Zerodha Access Token missing! Orders will fail.")
        except Exception as e:
            logger.error(f"Zerodha Init Error: {e}")

    def place_order(self, symbol, transaction_type, quantity=1):
        if not self.kite:
            logger.error("Zerodha Engine not initialized.")
            return

        try:
            from kiteconnect import KiteConnect
            order_id = self.kite.place_order(
                tradingsymbol=symbol,
                exchange=KiteConnect.EXCHANGE_NSE,
                transaction_type=transaction_type, # "BUY" or "SELL"
                quantity=quantity,
                variety=KiteConnect.VARIETY_REGULAR,
                order_type=KiteConnect.ORDER_TYPE_MARKET,
                product=KiteConnect.PRODUCT_MIS,
                validity=KiteConnect.VALIDITY_DAY
            )
            logger.success(f"Zerodha Order Placed: {order_id} for {symbol}")
        except Exception as e:
            logger.error(f"Zerodha Order Failed: {e}")

class IBKREngine(ExecutionEngine):
    def __init__(self):
        self.ib = None
        self.host = "127.0.0.1"
        self.port = int(os.getenv("IBKR_PORT", 7497)) # 7497 paper, 7496 live
        self.client_id = 1

    async def initialize(self):
        try:
            from ib_insync import IB
            self.ib = IB()
            await self.ib.connectAsync(self.host, self.port, self.client_id)
            logger.info(f"IBKR Engine Connected on port {self.port}")
        except Exception as e:
            logger.error(f"IBKR Connection Error: {e}. Is TWS/Gateway running?")

    def place_order(self, symbol, transaction_type, quantity=1):
        if not self.ib or not self.ib.isConnected():
            logger.error("IBKR Engine not connected.")
            return

        try:
            from ib_insync import Stock, MarketOrder
            contract = Stock(symbol, 'SMART', 'INR')
            order = MarketOrder(transaction_type, quantity)
            trade = self.ib.placeOrder(contract, order)
            logger.success(f"IBKR Order Placed: {trade.order.orderId} for {symbol}")
        except Exception as e:
            logger.error(f"IBKR Order Failed: {e}")
