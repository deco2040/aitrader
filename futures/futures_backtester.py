class FuturesBacktester:
    def __init__(self, initial_capital, commission_rate):
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.balance = initial_capital
        self.position = 0
        self.trades = []

    def buy(self, price, quantity):
        cost = price * quantity * (1 + self.commission_rate)
        if self.balance >= cost:
            self.balance -= cost
            self.position += quantity
            self.trades.append({'type': 'buy', 'price': price, 'quantity': quantity, 'cost': cost})
            print(f"Bought {quantity} at {price}. Balance: {self.balance}")
        else:
            print("Insufficient balance to buy.")

    def sell(self, price, quantity):
        if self.position >= quantity:
            revenue = price * quantity * (1 - self.commission_rate)
            self.balance += revenue
            self.position -= quantity
            self.trades.append({'type': 'sell', 'price': price, 'quantity': quantity, 'revenue': revenue})
            print(f"Sold {quantity} at {price}. Balance: {self.balance}")
        else:
            print("Insufficient position to sell.")

    def get_performance(self):
        return {
            'final_balance': self.balance,
            'total_trades': len(self.trades),
            'profit_loss': self.balance - self.initial_capital
        }

class SpotBacktester:
    def __init__(self, initial_capital, commission_rate):
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.balance = initial_capital
        self.holdings = {}
        self.trades = []

    def buy(self, asset, price, quantity):
        cost = price * quantity * (1 + self.commission_rate)
        if self.balance >= cost:
            self.balance -= cost
            self.holdings[asset] = self.holdings.get(asset, 0) + quantity
            self.trades.append({'type': 'buy', 'asset': asset, 'price': price, 'quantity': quantity, 'cost': cost})
            print(f"Bought {quantity} of {asset} at {price}. Balance: {self.balance}")
        else:
            print("Insufficient balance to buy.")

    def sell(self, asset, price, quantity):
        if asset in self.holdings and self.holdings[asset] >= quantity:
            revenue = price * quantity * (1 - self.commission_rate)
            self.balance += revenue
            self.holdings[asset] -= quantity
            if self.holdings[asset] == 0:
                del self.holdings[asset]
            self.trades.append({'type': 'sell', 'asset': asset, 'price': price, 'quantity': quantity, 'revenue': revenue})
            print(f"Sold {quantity} of {asset} at {price}. Balance: {self.balance}")
        else:
            print(f"Insufficient holdings of {asset} to sell.")

    def get_performance(self):
        return {
            'final_balance': self.balance,
            'total_trades': len(self.trades),
            'profit_loss': self.balance - self.initial_capital
        }