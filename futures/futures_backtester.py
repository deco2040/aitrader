from futures_claude_client import FuturesClaudeClient
from futures_config import *
from spot_claude_client import SpotClaudeClient
from spot_config import *

class TradingBot:
    def __init__(self):
        self.futures_client = FuturesClaudeClient()
        self.spot_client = SpotClaudeClient()

    def trade_futures(self, symbol, order_type, quantity, price):
        print(f"Futures trade executed: {order_type} {quantity} of {symbol} at {price}")
        self.futures_client.place_order(symbol, order_type, quantity, price)

    def trade_spot(self, symbol, order_type, quantity, price):
        print(f"Spot trade executed: {order_type} {quantity} of {symbol} at {price}")
        self.spot_client.place_order(symbol, order_type, quantity, price)

    def get_futures_balance(self):
        balance = self.futures_client.get_balance()
        print(f"Futures balance: {balance}")
        return balance

    def get_spot_balance(self):
        balance = self.spot_client.get_balance()
        print(f"Spot balance: {balance}")
        return balance

if __name__ == "__main__":
    bot = TradingBot()

    # Futures trading example
    bot.trade_futures("BTC/USD", "buy", 10, 50000)
    bot.get_futures_balance()

    # Spot trading example
    bot.trade_spot("ETH/USDT", "sell", 5, 3000)
    bot.get_spot_balance()