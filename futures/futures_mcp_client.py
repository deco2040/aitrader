class FuturesMCPClient:
    """
    This class is responsible for handling all interactions with the futures market data and trading operations.
    It provides methods to fetch futures prices, place orders, and manage futures positions.
    """

    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://api.example.com"):
        """
        Initializes the FuturesMCPClient with API credentials and the base URL for the API.

        Args:
            api_key: The API key for authentication.
            api_secret: The API secret for authentication.
            base_url: The base URL of the trading API.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        print("FuturesMCPClient initialized.")

    def fetch_futures_price(self, symbol: str) -> float:
        """
        Fetches the current price for a given futures symbol.

        Args:
            symbol: The futures symbol (e.g., "BTC-USD-230929").

        Returns:
            The current price of the futures contract.
        """
        print(f"Fetching futures price for {symbol}...")
        # Placeholder for actual API call to fetch futures price
        return 25000.50

    def place_futures_order(self, symbol: str, order_type: str, quantity: float, price: float = None) -> dict:
        """
        Places a futures order.

        Args:
            symbol: The futures symbol.
            order_type: The type of order (e.g., "limit", "market").
            quantity: The quantity to trade.
            price: The price for limit orders.

        Returns:
            A dictionary representing the placed order.
        """
        print(f"Placing {order_type} futures order for {quantity} of {symbol} at {price if price else 'market'}.")
        # Placeholder for actual API call to place futures order
        return {"order_id": "futures_order_123", "status": "open"}

    def get_futures_position(self, symbol: str) -> dict:
        """
        Retrieves the current position for a given futures symbol.

        Args:
            symbol: The futures symbol.

        Returns:
            A dictionary representing the futures position.
        """
        print(f"Getting futures position for {symbol}...")
        # Placeholder for actual API call to get futures position
        return {"symbol": symbol, "quantity": 1.5, "entry_price": 24800.0}

    def cancel_futures_order(self, order_id: str) -> dict:
        """
        Cancels an existing futures order.

        Args:
            order_id: The ID of the order to cancel.

        Returns:
            A dictionary indicating the result of the cancellation.
        """
        print(f"Cancelling futures order {order_id}...")
        # Placeholder for actual API call to cancel futures order
        return {"order_id": order_id, "status": "cancelled"}
    
    def execute_buy_order(self, symbol: str, amount: float) -> bool:
        """
        Execute a buy order for the given symbol and amount
        """
        print(f"Executing buy order: {symbol}, amount: {amount}")
        return True
    
    def execute_sell_order(self, symbol: str, amount: float) -> bool:
        """
        Execute a sell order for the given symbol and amount
        """
        print(f"Executing sell order: {symbol}, amount: {amount}")
        return True
    
    def get_position(self, symbol: str) -> dict:
        """
        Get position for the given symbol
        """
        return {"symbol": symbol, "size": 0, "avg_entry_price": 0}
    
    def get_market_data(self, symbol: str) -> dict:
        """
        Get market data for the given symbol
        """
        return {"symbol": symbol, "price": 45000.0, "volume": 1000000}
    
    def get_account_balance(self) -> dict:
        """
        Get account balance information
        """
        return {"available": 10000.0, "total": 10000.0}

class FuturesMarketData:
    """
    Handles the retrieval and processing of futures market data.
    This includes historical data, real-time feeds, and order book information.
    """

    def __init__(self, data_source_url: str):
        """
        Initializes the FuturesMarketData with a data source URL.

        Args:
            data_source_url: The URL to fetch market data from.
        """
        self.data_source_url = data_source_url
        print("FuturesMarketData initialized.")

    def get_historical_futures_data(self, symbol: str, start_time: int, end_time: int) -> list:
        """
        Fetches historical market data for a futures contract.

        Args:
            symbol: The futures symbol.
            start_time: The start timestamp for the data.
            end_time: The end timestamp for the data.

        Returns:
            A list of historical data points.
        """
        print(f"Fetching historical futures data for {symbol} from {start_time} to {end_time}.")
        # Placeholder for actual API call to get historical data
        return [{"time": t, "price": 24000 + i * 10} for i, t in enumerate(range(start_time, end_time, 3600))]

    def get_realtime_futures_feed(self, symbol: str) -> list:
        """
        Connects to a real-time feed for futures price updates.

        Args:
            symbol: The futures symbol to subscribe to.

        Returns:
            A list of recent price updates.
        """
        print(f"Connecting to real-time futures feed for {symbol}.")
        # Placeholder for WebSocket or stream connection
        return [{"time": 1678886400, "price": 25100.0}]

    def get_futures_order_book(self, symbol: str) -> dict:
        """
        Retrieves the order book for a given futures symbol.

        Args:
            symbol: The futures symbol.

        Returns:
            A dictionary representing the order book (bids and asks).
        """
        print(f"Fetching futures order book for {symbol}.")
        # Placeholder for actual API call to get order book
        return {"symbol": symbol, "bids": [[25000.0, 10.5]], "asks": [[25001.0, 8.2]]}

class FuturesTradingStrategy:
    """
    Implements various trading strategies for the futures market.
    This class focuses on the logic and decision-making for trades.
    """

    def __init__(self, client: FuturesMCPClient, data_handler: FuturesMarketData):
        """
        Initializes the FuturesTradingStrategy with a client and data handler.

        Args:
            client: An instance of FuturesMCPClient.
            data_handler: An instance of FuturesMarketData.
        """
        self.client = client
        self.data_handler = data_handler
        print("FuturesTradingStrategy initialized.")

    def execute_moving_average_strategy(self, symbol: str, short_window: int, long_window: int):
        """
        Executes a moving average crossover strategy for futures trading.

        Args:
            symbol: The futures symbol.
            short_window: The lookback period for the short moving average.
            long_window: The lookback period for the long moving average.
        """
        print(f"Executing moving average strategy for {symbol} with windows {short_window} and {long_window}.")
        historical_data = self.data_handler.get_historical_futures_data(symbol, 0, 0) # Simplified time range
        if len(historical_data) < long_window:
            print("Not enough data to execute strategy.")
            return

        # Calculate moving averages (simplified)
        short_ma = sum([d['price'] for d in historical_data[-short_window:]]) / short_window
        long_ma = sum([d['price'] for d in historical_data[-long_window:]]) / long_window

        current_price = self.data_handler.get_realtime_futures_feed(symbol)[0]['price']

        if short_ma > long_ma and current_price > short_ma:
            print("Golden Cross detected. Consider buying futures.")
            # Example: place buy order
            # self.client.place_futures_order(symbol, "limit", 1.0, current_price * 0.99)
        elif short_ma < long_ma and current_price < short_ma:
            print("Death Cross detected. Consider selling futures.")
            # Example: place sell order
            # self.client.place_futures_order(symbol, "limit", 1.0, current_price * 1.01)
        else:
            print("No clear trading signal.")

class SpotMCPClient:
    """
    This class is responsible for handling all interactions with the spot market data and trading operations.
    It provides methods to fetch spot prices, place orders, and manage spot positions.
    """

    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://api.example.com"):
        """
        Initializes the SpotMCPClient with API credentials and the base URL for the API.

        Args:
            api_key: The API key for authentication.
            api_secret: The API secret for authentication.
            base_url: The base URL of the trading API.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        print("SpotMCPClient initialized.")

    def fetch_spot_price(self, symbol: str) -> float:
        """
        Fetches the current price for a given spot symbol.

        Args:
            symbol: The spot symbol (e.g., "BTC-USD").

        Returns:
            The current price of the asset.
        """
        print(f"Fetching spot price for {symbol}...")
        # Placeholder for actual API call to fetch spot price
        return 25000.50

    def place_spot_order(self, symbol: str, order_type: str, quantity: float, price: float = None) -> dict:
        """
        Places a spot order.

        Args:
            symbol: The spot symbol.
            order_type: The type of order (e.g., "limit", "market").
            quantity: The quantity to trade.
            price: The price for limit orders.

        Returns:
            A dictionary representing the placed order.
        """
        print(f"Placing {order_type} spot order for {quantity} of {symbol} at {price if price else 'market'}.")
        # Placeholder for actual API call to place spot order
        return {"order_id": "spot_order_123", "status": "filled"}

    def get_spot_position(self, symbol: str) -> dict:
        """
        Retrieves the current holdings for a given spot symbol.

        Args:
            symbol: The spot symbol.

        Returns:
            A dictionary representing the spot position.
        """
        print(f"Getting spot position for {symbol}...")
        # Placeholder for actual API call to get spot position
        return {"symbol": symbol, "quantity": 5.0, "average_buy_price": 24500.0}

    def cancel_spot_order(self, order_id: str) -> dict:
        """
        Cancels an existing spot order.

        Args:
            order_id: The ID of the order to cancel.

        Returns:
            A dictionary indicating the result of the cancellation.
        """
        print(f"Cancelling spot order {order_id}...")
        # Placeholder for actual API call to cancel spot order
        return {"order_id": order_id, "status": "cancelled"}

class SpotMarketData:
    """
    Handles the retrieval and processing of spot market data.
    This includes historical data, real-time feeds, and order book information.
    """

    def __init__(self, data_source_url: str):
        """
        Initializes the SpotMarketData with a data source URL.

        Args:
            data_source_url: The URL to fetch market data from.
        """
        self.data_source_url = data_source_url
        print("SpotMarketData initialized.")

    def get_historical_spot_data(self, symbol: str, start_time: int, end_time: int) -> list:
        """
        Fetches historical market data for a spot asset.

        Args:
            symbol: The spot symbol.
            start_time: The start timestamp for the data.
            end_time: The end timestamp for the data.

        Returns:
            A list of historical data points.
        """
        print(f"Fetching historical spot data for {symbol} from {start_time} to {end_time}.")
        # Placeholder for actual API call to get historical data
        return [{"time": t, "price": 24000 + i * 5} for i, t in enumerate(range(start_time, end_time, 1800))]

    def get_realtime_spot_feed(self, symbol: str) -> list:
        """
        Connects to a real-time feed for spot price updates.

        Args:
            symbol: The spot symbol to subscribe to.

        Returns:
            A list of recent price updates.
        """
        print(f"Connecting to real-time spot feed for {symbol}.")
        # Placeholder for WebSocket or stream connection
        return [{"time": 1678886400, "price": 25100.0}]

    def get_spot_order_book(self, symbol: str) -> dict:
        """
        Retrieves the order book for a given spot symbol.

        Args:
            symbol: The spot symbol.

        Returns:
            A dictionary representing the order book (bids and asks).
        """
        print(f"Fetching spot order book for {symbol}.")
        # Placeholder for actual API call to get order book
        return {"symbol": symbol, "bids": [[25000.0, 10.5]], "asks": [[25001.0, 8.2]]}

class SpotTradingStrategy:
    """
    Implements various trading strategies for the spot market.
    This class focuses on the logic and decision-making for trades.
    """

    def __init__(self, client: SpotMCPClient, data_handler: SpotMarketData):
        """
        Initializes the SpotTradingStrategy with a client and data handler.

        Args:
            client: An instance of SpotMCPClient.
            data_handler: An instance of SpotMarketData.
        """
        self.client = client
        self.data_handler = data_handler
        print("SpotTradingStrategy initialized.")

    def execute_rsi_strategy(self, symbol: str, window: int = 14, overbought: int = 70, oversold: int = 30):
        """
        Executes a Relative Strength Index (RSI) strategy for spot trading.

        Args:
            symbol: The spot symbol.
            window: The lookback period for RSI calculation.
            overbought: The RSI level considered overbought.
            oversold: The RSI level considered oversold.
        """
        print(f"Executing RSI strategy for {symbol} with window {window}, overbought {overbought}, oversold {oversold}.")
        historical_data = self.data_handler.get_historical_spot_data(symbol, 0, 0) # Simplified time range
        if len(historical_data) < window + 1:
            print("Not enough data to calculate RSI.")
            return

        # Calculate RSI (simplified)
        price_changes = [historical_data[i]['price'] - historical_data[i-1]['price'] for i in range(1, len(historical_data))]
        gains = [pc for pc in price_changes if pc > 0]
        losses = [abs(pc) for pc in price_changes if pc < 0]

        avg_gain = sum(gains[-window:]) / window
        avg_loss = sum(losses[-window:]) / window

        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

        current_price = self.data_handler.get_realtime_spot_feed(symbol)[0]['price']

        if rsi > overbought:
            print(f"RSI({rsi:.2f}) is overbought. Consider selling {symbol}.")
            # Example: place sell order
            # self.client.place_spot_order(symbol, "limit", 0.5, current_price * 0.98)
        elif rsi < oversold:
            print(f"RSI({rsi:.2f}) is oversold. Consider buying {symbol}.")
            # Example: place buy order
            # self.client.place_spot_order(symbol, "limit", 0.5, current_price * 1.02)
        else:
            print(f"RSI({rsi:.2f}) is neutral.")


if __name__ == "__main__":
    # Example Usage for Futures
    futures_client = FuturesMCPClient("future_api_key", "future_api_secret")
    futures_data = FuturesMarketData("https://futures.api.example.com")
    futures_strategy = FuturesTradingStrategy(futures_client, futures_data)

    btc_futures_symbol = "BTC-USD-230929"
    print(f"\n--- Futures Operations for {btc_futures_symbol} ---")
    futures_price = futures_client.fetch_futures_price(btc_futures_symbol)
    print(f"Current futures price: {futures_price}")

    futures_position = futures_client.get_futures_position(btc_futures_symbol)
    print(f"Futures position: {futures_position}")

    futures_strategy.execute_moving_average_strategy(btc_futures_symbol, short_window=10, long_window=30)

    # Example Usage for Spot
    spot_client = SpotMCPClient("spot_api_key", "spot_api_secret")
    spot_data = SpotMarketData("https://spot.api.example.com")
    spot_strategy = SpotTradingStrategy(spot_client, spot_data)

    eth_spot_symbol = "ETH-USD"
    print(f"\n--- Spot Operations for {eth_spot_symbol} ---")
    spot_price = spot_client.fetch_spot_price(eth_spot_symbol)
    print(f"Current spot price: {spot_price}")

    spot_position = spot_client.get_spot_position(eth_spot_symbol)
    print(f"Spot position: {spot_position}")

    spot_strategy.execute_rsi_strategy(eth_spot_symbol, window=14, overbought=70, oversold=30)

class FuturesMCPClient:
    """Futures MCP Client for order execution and data retrieval"""
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.positions = {}
        self.balance = {"available": 10000.0, "total": 10000.0}
    
    def execute_buy_order(self, symbol: str, amount: float) -> bool:
        """Execute buy order"""
        print(f"🟢 Executing BUY order: {symbol}, Amount: {amount}")
        current_size = self.positions.get(symbol, 0)
        self.positions[symbol] = current_size + amount
        self.balance["available"] -= amount * 0.1  # Assuming margin requirement
        return True
    
    def execute_sell_order(self, symbol: str, amount: float) -> bool:
        """Execute sell order"""
        print(f"🔴 Executing SELL order: {symbol}, Amount: {amount}")
        current_size = self.positions.get(symbol, 0)
        self.positions[symbol] = current_size - amount
        self.balance["available"] += amount * 0.1  # Return margin
        return True
    
    def get_position(self, symbol: str) -> dict:
        """Get current position for symbol"""
        size = self.positions.get(symbol, 0)
        return {
            "symbol": symbol,
            "size": size,
            "avg_entry_price": 45000.0,
            "unrealized_pnl": size * 50  # Dummy PnL
        }
    
    def get_market_data(self, symbol: str) -> dict:
        """Get market data for symbol"""
        return {
            "symbol": symbol,
            "price": 45000.0,
            "volume": 1500000000,
            "24h_change": 2.5,
            "bid": 44995.0,
            "ask": 45005.0
        }
    
    def get_account_balance(self) -> dict:
        """Get account balance"""
        return self.balance