class SpotClaudeClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_balance(self, currency: str) -> float:
        """
        Fetches the balance for a given currency.
        """
        # Placeholder for actual API call to get balance
        print(f"Fetching balance for {currency} with API key {self.api_key[:4]}...")
        if currency == "USD":
            return 1000.50
        elif currency == "BTC":
            return 0.12345
        else:
            return 0.0

    def place_order(self, symbol: str, quantity: float, price: float, order_type: str) -> dict:
        """
        Places an order on the spot market.
        """
        print(f"Placing {order_type} order for {quantity} of {symbol} at {price} on spot market.")
        # Placeholder for actual API call to place order
        order_id = f"SPOT_{symbol.upper()}_{int(quantity)}_{int(price)}_{order_type.upper()}"
        return {"order_id": order_id, "status": "pending"}

    def cancel_order(self, order_id: str) -> dict:
        """
        Cancels a previously placed spot order.
        """
        print(f"Cancelling spot order: {order_id}")
        # Placeholder for actual API call to cancel order
        return {"order_id": order_id, "status": "cancelled"}

    def get_order_status(self, order_id: str) -> dict:
        """
        Retrieves the status of a spot order.
        """
        print(f"Getting status for spot order: {order_id}")
        # Placeholder for actual API call to get order status
        if "SPOT" in order_id:
            return {"order_id": order_id, "status": "filled"}
        else:
            return {"order_id": order_id, "status": "not_found"}

# Example Usage:
# spot_client = SpotClaudeClient("your_spot_api_key")
# balance = spot_client.get_balance("USD")
# print(f"USD Balance: {balance}")
# order = spot_client.place_order("BTCUSDT", 0.1, 50000, "limit")
# print(f"Order placed: {order}")
# status = spot_client.get_order_status(order['order_id'])
# print(f"Order status: {status}")