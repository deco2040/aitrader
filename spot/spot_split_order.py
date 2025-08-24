class SpotSplitOrder:
    def __init__(self, order_id, symbol, price, quantity, order_type, timestamp):
        self.order_id = order_id
        self.symbol = symbol
        self.price = price
        self.quantity = quantity
        self.order_type = order_type
        self.timestamp = timestamp

    def __str__(self):
        return f"SpotSplitOrder(order_id={self.order_id}, symbol={self.symbol}, price={self.price}, quantity={self.quantity}, order_type={self.order_type}, timestamp={self.timestamp})"

    def get_order_details(self):
        return {
            "order_id": self.order_id,
            "symbol": self.symbol,
            "price": self.price,
            "quantity": self.quantity,
            "order_type": self.order_type,
            "timestamp": self.timestamp
        }

    def update_quantity(self, new_quantity):
        self.quantity = new_quantity

    def update_price(self, new_price):
        self.price = new_price

    def is_buy_order(self):
        return self.order_type == "BUY"

    def is_sell_order(self):
        return self.order_type == "SELL"