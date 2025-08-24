import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

class SpotBacktester:
    def __init__(self, symbol=None, start_date=None, end_date=None, initial_capital=10000, commission_rate=0.001, slippage_rate=0.001):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        self.trades = []
        self.balance = initial_capital
        self.holdings = {}

        if symbol and start_date and end_date:
            # 히스토리컬 백테스팅용
            self.equity = pd.DataFrame(index=self.get_data().index)
            self.equity['holdings'] = 0.0
            self.equity['cash'] = self.initial_capital
            self.equity['total'] = self.initial_capital
            self.equity['returns'] = 0.0

    def get_data(self):
        """야후 파이낸스에서 데이터 가져오기"""
        if not self.symbol:
            print("Symbol not provided for data download")
            return pd.DataFrame()

        try:
            print(f"Downloading data for {self.symbol} from {self.start_date} to {self.end_date}")
            df = yf.download(self.symbol, start=self.start_date, end=self.end_date, progress=False)
            if df.empty:
                print(f"No data found for symbol {self.symbol}")
            else:
                print(f"Successfully downloaded {len(df)} data points")
            return df
        except Exception as e:
            print(f"Error downloading data for {self.symbol}: {e}")
            return pd.DataFrame()

    def buy(self, asset_or_price, price_or_quantity, quantity=None):
        """매수 주문"""
        # 입력값 타입 검증
        try:
            if quantity is None:
                # 3개 매개변수 모드: asset, price, quantity
                asset = asset_or_price
                price = float(price_or_quantity) if price_or_quantity is not None else 0.0
                quantity = 0.0  # quantity가 None이면 0으로 처리
                print(f"Warning: quantity is None for {asset}")
                return False
            else:
                # 히스토리컬 백테스팅용: price, quantity
                if isinstance(asset_or_price, str):
                    # 3개 매개변수: asset, price, quantity
                    asset = asset_or_price
                    price = float(price_or_quantity) if price_or_quantity is not None else 0.0
                    quantity = float(quantity) if quantity is not None else 0.0
                else:
                    # 히스토리컬 백테스팅: price, quantity
                    asset = 'position'
                    price = float(asset_or_price) if asset_or_price is not None else 0.0
                    quantity = float(price_or_quantity) if price_or_quantity is not None else 0.0
        except (ValueError, TypeError) as e:
            print(f"Invalid input types in buy(): {e}")
            return False

        if price <= 0 or quantity <= 0:
            print(f"Invalid price ({price}) or quantity ({quantity})")
            return False

        cost = price * quantity * (1 + self.commission_rate)
        
        if self.balance >= cost:
            self.balance -= cost
            self.holdings[asset] = self.holdings.get(asset, 0) + quantity
            self.trades.append({
                'type': 'buy', 
                'asset': asset, 
                'price': price, 
                'quantity': quantity, 
                'cost': cost,
                'timestamp': datetime.now()
            })
            print(f"Bought {quantity} of {asset} at ${price}. Balance: ${self.balance:.2f}")
            return True
        else:
            print(f"Insufficient balance. Required: ${cost:.2f}, Available: ${self.balance:.2f}")
            return False

    def sell(self, asset_or_price, price_or_quantity, quantity=None):
        """매도 주문"""
        # 입력값 타입 검증
        try:
            if quantity is None:
                # quantity가 None이면 오류
                asset = asset_or_price
                price = float(price_or_quantity) if price_or_quantity is not None else 0.0
                quantity = 0.0
                print(f"Warning: quantity is None for {asset}")
                return False
            else:
                if isinstance(asset_or_price, str):
                    # 3개 매개변수: asset, price, quantity
                    asset = asset_or_price
                    price = float(price_or_quantity) if price_or_quantity is not None else 0.0
                    quantity = float(quantity) if quantity is not None else 0.0
                else:
                    # 히스토리컬 백테스팅: price, quantity
                    asset = 'position'
                    price = float(asset_or_price) if asset_or_price is not None else 0.0
                    quantity = float(price_or_quantity) if price_or_quantity is not None else 0.0
        except (ValueError, TypeError) as e:
            print(f"Invalid input types in sell(): {e}")
            return False

        if price <= 0 or quantity <= 0:
            print(f"Invalid price ({price}) or quantity ({quantity})")
            return False

        current_holdings = self.holdings.get(asset, 0)
        if current_holdings >= quantity:
            revenue = price * quantity * (1 - self.commission_rate)
            self.balance += revenue
            self.holdings[asset] -= quantity
            if self.holdings[asset] == 0:
                del self.holdings[asset]
            self.trades.append({
                'type': 'sell', 
                'asset': asset, 
                'price': price, 
                'quantity': quantity, 
                'revenue': revenue,
                'timestamp': datetime.now()
            })
            print(f"Sold {quantity} of {asset} at ${price}. Balance: ${self.balance:.2f}")
            return True
        else:
            print(f"Insufficient holdings of {asset}. Required: {quantity}, Available: {current_holdings}")
            return False

    def backtest(self):
        """전체 백테스팅 실행"""
        if not self.symbol:
            print("Symbol not set for historical backtesting")
            return None

        data = self.get_data()
        if data.empty:
            print("No data available")
            return None

        signals = self.generate_signals(data)
        self.execute_trades(data, signals)
        self.calculate_equity(data)
        return self.equity

    def generate_signals(self, data):
        """거래 신호 생성 (이동평균 교차 전략)"""
        short_window = 50
        long_window = 200

        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0.0

        signals['short_mavg'] = data['Close'].rolling(window=short_window, min_periods=1).mean()
        signals['long_mavg'] = data['Close'].rolling(window=long_window, min_periods=1).mean()

        # pandas 경고 해결: .loc 사용
        mask = signals.index[short_window:]
        signals.loc[mask, 'signal'] = np.where(
            signals.loc[mask, 'short_mavg'] > signals.loc[mask, 'long_mavg'], 
            1.0, 0.0
        )
        signals['positions'] = signals['signal'].diff()

        return signals

    def execute_trades(self, data, signals):
        """거래 실행"""
        for i in range(1, len(signals)):
            if signals['positions'].iloc[i] == 1:  # Buy signal
                self.enter_trade(data, i, 'long')
            elif signals['positions'].iloc[i] == -1:  # Sell signal
                self.exit_trade(data, i, 'long')

    def enter_trade(self, data, index, order_type):
        """포지션 진입"""
        current_price = data['Close'].iloc[index]
        date = data.index[index]

        if order_type == 'long' and self.equity['cash'].iloc[index-1] > 0:
            order_size = self.equity['cash'].iloc[index-1] / current_price
            cost = order_size * current_price * (1 + self.commission_rate)
            self.trades.append({
                'date': date, 
                'type': 'buy', 
                'price': current_price, 
                'size': order_size
            })
            self.equity.loc[date, 'holdings'] = order_size
            self.equity.loc[date, 'cash'] = self.equity['cash'].iloc[index-1] - cost

    def exit_trade(self, data, index, order_type):
        """포지션 종료"""
        current_price = data['Close'].iloc[index]
        date = data.index[index]

        if order_type == 'long' and self.equity['holdings'].iloc[index-1] > 0:
            order_size = self.equity['holdings'].iloc[index-1]
            revenue = order_size * current_price * (1 - self.commission_rate)
            self.trades.append({
                'date': date, 
                'type': 'sell', 
                'price': current_price, 
                'size': order_size
            })
            self.equity.loc[date, 'holdings'] = 0
            self.equity.loc[date, 'cash'] = self.equity['cash'].iloc[index-1] + revenue

    def calculate_equity(self, data):
        """자산 곡선 계산"""
        for i in range(len(data)):
            date = data.index[i]
            current_price = data['Close'].iloc[i]

            if i > 0:
                self.equity.loc[date, 'holdings'] = self.equity['holdings'].iloc[i-1]
                self.equity.loc[date, 'cash'] = self.equity['cash'].iloc[i-1]

            self.equity.loc[date, 'total'] = (
                self.equity['holdings'].iloc[i] * current_price + 
                self.equity['cash'].iloc[i]
            )

        self.equity['returns'] = self.equity['total'].pct_change().fillna(0)

    def get_performance(self):
        """성과 분석"""
        if hasattr(self, 'equity') and not self.equity.empty:
            # 히스토리컬 백테스팅 결과
            final_value = self.equity['total'].iloc[-1]
            return {
                'initial_capital': self.initial_capital,
                'final_value': final_value,
                'total_trades': len(self.trades),
                'profit_loss': final_value - self.initial_capital,
                'returns': self.equity['returns'].tolist()
            }
        else:
            # 실시간 거래 결과 - 타입 안전성 개선
            total_holdings_value = 0.0
            default_prices = {"BTC": 45000.0, "ETH": 3000.0, "SOL": 150.0, "position": 45000.0}
            
            for asset, quantity in self.holdings.items():
                try:
                    # None 체크 및 타입 변환
                    if quantity is None or quantity == 0:
                        continue
                    
                    # 문자열, 리스트 등 잘못된 타입 체크
                    if isinstance(quantity, (str, list, dict)):
                        print(f"Warning: Invalid quantity type for {asset}: {type(quantity)}")
                        continue
                        
                    quantity_float = float(quantity)
                    
                    if quantity_float > 0:
                        price = default_prices.get(asset, 100.0)
                        total_holdings_value += quantity_float * price
                        
                except (ValueError, TypeError) as e:
                    print(f"Warning: Invalid quantity for {asset}: {quantity}, error: {e}")
                    continue

            # balance 안전 변환
            try:
                balance_float = float(self.balance) if self.balance is not None else 0.0
            except (ValueError, TypeError):
                balance_float = 0.0
            
            return {
                'initial_capital': float(self.initial_capital),
                'final_balance': balance_float,
                'holdings_value': total_holdings_value,
                'total_value': balance_float + total_holdings_value,
                'total_trades': len(self.trades),
                'profit_loss': (balance_float + total_holdings_value) - float(self.initial_capital)
            }

# 하위 호환성을 위한 별칭
AggressiveBacktester = SpotBacktester