class AggressiveBacktester:
    def __init__(self, symbol, start_date, end_date, initial_capital, commission_rate, slippage_rate):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        self.trades = []
        self.equity = pd.DataFrame(index=self.get_data().index)
        self.equity['holdings'] = 0.0
        self.equity['cash'] = self.initial_capital
        self.equity['total'] = self.initial_capital
        self.equity['returns'] = 0.0

    def get_data(self):
        df = yf.download(self.symbol, start=self.start_date, end=self.end_date)
        return df

    def backtest(self):
        data = self.get_data()
        signals = self.generate_signals(data)
        self.execute_trades(data, signals)
        self.calculate_equity(data)
        return self.equity

    def generate_signals(self, data):
        # Implement your trading strategy here
        # For example, a simple moving average crossover strategy
        short_window = 50
        long_window = 200

        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0.0

        signals['short_mavg'] = data['Close'].rolling(window=short_window, min_periods=1).mean()
        signals['long_mavg'] = data['Close'].rolling(window=long_window, min_periods=1).mean()

        signals['signal'][short_window:] = np.where(signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:], 1.0, 0.0)
        signals['positions'] = signals['signal'].diff()

        return signals

    def execute_trades(self, data, signals):
        for i in range(len(signals)):
            if signals['positions'].iloc[i] == 1:  # Buy signal
                self.enter_trade(data, i, 'long')
            elif signals['positions'].iloc[i] == -1:  # Sell signal
                self.enter_trade(data, i, 'short')

    def enter_trade(self, data, index, order_type):
        current_price = data['Close'].iloc[index]
        date = data.index[index]
        order_size = 0
        cost = 0

        if order_type == 'long':
            if self.equity['cash'].iloc[index-1] > 0:
                order_size = self.equity['cash'].iloc[index-1] / current_price
                cost = order_size * current_price * (1 + self.commission_rate)
                self.trades.append({'date': date, 'type': 'buy', 'price': current_price, 'size': order_size})
                self.equity.loc[date, 'holdings'] = order_size
                self.equity.loc[date, 'cash'] = self.equity['cash'].iloc[index-1] - cost
            else:
                pass # Not enough cash to buy

        elif order_type == 'short':
            # For simplicity, we are not implementing short selling in this example.
            # If you want to implement short selling, you would need to manage short positions and their PnL.
            pass

    def exit_trade(self, data, index, order_type):
        current_price = data['Close'].iloc[index]
        date = data.index[index]

        if order_type == 'long':
            if self.equity['holdings'].iloc[index-1] > 0:
                order_size = self.equity['holdings'].iloc[index-1]
                revenue = order_size * current_price * (1 - self.commission_rate)
                self.trades.append({'date': date, 'type': 'sell', 'price': current_price, 'size': order_size})
                self.equity.loc[date, 'holdings'] = 0
                self.equity.loc[date, 'cash'] = self.equity['cash'].iloc[index-1] + revenue
            else:
                pass # No holdings to sell

        elif order_type == 'short':
            # Not implementing short selling exit here
            pass

    def calculate_equity(self, data):
        for i in range(len(data)):
            date = data.index[i]
            current_price = data['Close'].iloc[i]

            if i > 0:
                self.equity.loc[date, 'holdings'] = self.equity['holdings'].iloc[i-1]
                self.equity.loc[date, 'cash'] = self.equity['cash'].iloc[i-1]
                self.equity.loc[date, 'returns'] = (self.equity['holdings'].iloc[i-1] * current_price) - (self.equity['holdings'].iloc[i-1] * data['Close'].iloc[i-1])

            self.equity.loc[date, 'total'] = self.equity['holdings'].iloc[i] * current_price + self.equity['cash'].iloc[i]

        self.equity['returns'] = self.equity['total'].pct_change().fillna(0)


class SpotBacktester:
    def __init__(self, symbol, start_date, end_date, initial_capital, commission_rate, slippage_rate):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        self.trades = []
        self.equity = pd.DataFrame(index=self.get_data().index)
        self.equity['holdings'] = 0.0
        self.equity['cash'] = self.initial_capital
        self.equity['total'] = self.initial_capital
        self.equity['returns'] = 0.0

    def get_data(self):
        df = yf.download(self.symbol, start=self.start_date, end=self.end_date)
        return df

    def backtest(self):
        data = self.get_data()
        signals = self.generate_signals(data)
        self.execute_trades(data, signals)
        self.calculate_equity(data)
        return self.equity

    def generate_signals(self, data):
        # Implement your trading strategy here
        # For example, a simple moving average crossover strategy
        short_window = 50
        long_window = 200

        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0.0

        signals['short_mavg'] = data['Close'].rolling(window=short_window, min_periods=1).mean()
        signals['long_mavg'] = data['Close'].rolling(window=long_window, min_periods=1).mean()

        signals['signal'][short_window:] = np.where(signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:], 1.0, 0.0)
        signals['positions'] = signals['signal'].diff()

        return signals

    def execute_trades(self, data, signals):
        for i in range(len(signals)):
            if signals['positions'].iloc[i] == 1:  # Buy signal
                self.enter_trade(data, i, 'long')
            elif signals['positions'].iloc[i] == -1:  # Sell signal
                self.exit_trade(data, i, 'short') # Corrected from enter_trade to exit_trade for sell signal

    def enter_trade(self, data, index, order_type):
        current_price = data['Close'].iloc[index]
        date = data.index[index]
        order_size = 0
        cost = 0

        if order_type == 'long':
            if self.equity['cash'].iloc[index-1] > 0:
                order_size = self.equity['cash'].iloc[index-1] / current_price
                cost = order_size * current_price * (1 + self.commission_rate)
                self.trades.append({'date': date, 'type': 'buy', 'price': current_price, 'size': order_size})
                self.equity.loc[date, 'holdings'] = order_size
                self.equity.loc[date, 'cash'] = self.equity['cash'].iloc[index-1] - cost
            else:
                pass # Not enough cash to buy

        elif order_type == 'short':
            # For simplicity, we are not implementing short selling in this example.
            # If you want to implement short selling, you would need to manage short positions and their PnL.
            pass

    def exit_trade(self, data, index, order_type):
        current_price = data['Close'].iloc[index]
        date = data.index[index]

        if order_type == 'long':
            if self.equity['holdings'].iloc[index-1] > 0:
                order_size = self.equity['holdings'].iloc[index-1]
                revenue = order_size * current_price * (1 - self.commission_rate)
                self.trades.append({'date': date, 'type': 'sell', 'price': current_price, 'size': order_size})
                self.equity.loc[date, 'holdings'] = 0
                self.equity.loc[date, 'cash'] = self.equity['cash'].iloc[index-1] + revenue
            else:
                pass # No holdings to sell

        elif order_type == 'short':
            # Not implementing short selling exit here
            pass

    def calculate_equity(self, data):
        for i in range(len(data)):
            date = data.index[i]
            current_price = data['Close'].iloc[i]

            if i > 0:
                self.equity.loc[date, 'holdings'] = self.equity['holdings'].iloc[i-1]
                self.equity.loc[date, 'cash'] = self.equity['cash'].iloc[i-1]
                self.equity.loc[date, 'returns'] = (self.equity['holdings'].iloc[i-1] * current_price) - (self.equity['holdings'].iloc[i-1] * data['Close'].iloc[i-1])

            self.equity.loc[date, 'total'] = self.equity['holdings'].iloc[i] * current_price + self.equity['cash'].iloc[i]

        self.equity['returns'] = self.equity['total'].pct_change().fillna(0)