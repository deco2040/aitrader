
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
        self.equity = None

        if symbol and start_date and end_date:
            # 히스토리컬 백테스팅용 초기화
            try:
                data = self.get_data()
                if not data.empty:
                    self.equity = pd.DataFrame(index=data.index)
                    self.equity['holdings'] = 0.0
                    self.equity['cash'] = float(self.initial_capital)
                    self.equity['total'] = float(self.initial_capital)
                    self.equity['returns'] = 0.0
            except Exception as e:
                print(f"Warning: Could not initialize historical data: {e}")
                self.equity = None

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
        """매수 주문 - 타입 안전성 강화"""
        try:
            # 입력 파라미터 정규화
            if quantity is None:
                if isinstance(asset_or_price, str):
                    # asset만 제공된 경우
                    print(f"Warning: Incomplete parameters for {asset_or_price}")
                    return False
                else:
                    # 히스토리컬 백테스팅: price, quantity
                    asset = 'position'
                    price = float(asset_or_price) if asset_or_price is not None else 0.0
                    quantity = float(price_or_quantity) if price_or_quantity is not None else 0.0
            else:
                # 표준 모드: asset, price, quantity
                asset = str(asset_or_price)
                price = float(price_or_quantity) if price_or_quantity is not None else 0.0
                quantity = float(quantity) if quantity is not None else 0.0

        except (ValueError, TypeError) as e:
            print(f"Invalid input types in buy(): {e}")
            return False

        # 유효성 검증
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
        """매도 주문 - 타입 안전성 강화"""
        try:
            # 입력 파라미터 정규화
            if quantity is None:
                if isinstance(asset_or_price, str):
                    print(f"Warning: Incomplete parameters for {asset_or_price}")
                    return False
                else:
                    # 히스토리컬 백테스팅: price, quantity
                    asset = 'position'
                    price = float(asset_or_price) if asset_or_price is not None else 0.0
                    quantity = float(price_or_quantity) if price_or_quantity is not None else 0.0
            else:
                # 표준 모드: asset, price, quantity
                asset = str(asset_or_price)
                price = float(price_or_quantity) if price_or_quantity is not None else 0.0
                quantity = float(quantity) if quantity is not None else 0.0

        except (ValueError, TypeError) as e:
            print(f"Invalid input types in sell(): {e}")
            return False

        # 유효성 검증
        if price <= 0 or quantity <= 0:
            print(f"Invalid price ({price}) or quantity ({quantity})")
            return False

        current_holdings = self.holdings.get(asset, 0)
        if current_holdings >= quantity:
            revenue = price * quantity * (1 - self.commission_rate)
            self.balance += revenue
            self.holdings[asset] -= quantity
            if self.holdings[asset] <= 0:
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
        """전체 백테스팅 실행 - 오류 수정"""
        if not self.symbol:
            print("Symbol not set for historical backtesting")
            return None

        try:
            data = self.get_data()
            if data.empty:
                print("No data available")
                return None

            # 안전한 백테스팅 실행
            signals = self.generate_signals(data)
            self.execute_trades_safe(data, signals)
            self.calculate_equity_safe(data)
            return self.equity

        except Exception as e:
            print(f"Backtesting failed: {e}")
            return None

    def generate_signals(self, data):
        """거래 신호 생성 - 안정성 개선"""
        try:
            short_window = 5  # 짧은 윈도우로 변경
            long_window = 10  # 짧은 윈도우로 변경

            signals = pd.DataFrame(index=data.index)
            signals['signal'] = 0.0

            # 이동평균 계산
            signals['short_mavg'] = data['Close'].rolling(window=short_window, min_periods=1).mean()
            signals['long_mavg'] = data['Close'].rolling(window=long_window, min_periods=1).mean()

            # 신호 생성 - 안전한 방식
            for i in range(long_window, len(signals)):
                if signals.iloc[i]['short_mavg'] > signals.iloc[i]['long_mavg']:
                    signals.iloc[i, signals.columns.get_loc('signal')] = 1.0
                else:
                    signals.iloc[i, signals.columns.get_loc('signal')] = 0.0

            signals['positions'] = signals['signal'].diff()
            return signals

        except Exception as e:
            print(f"Signal generation failed: {e}")
            # 기본 신호 반환
            signals = pd.DataFrame(index=data.index)
            signals['signal'] = 0.0
            signals['positions'] = 0.0
            return signals

    def execute_trades_safe(self, data, signals):
        """안전한 거래 실행"""
        try:
            for i in range(1, len(signals)):
                if signals['positions'].iloc[i] == 1:  # Buy signal
                    self.enter_trade_safe(data, i, 'long')
                elif signals['positions'].iloc[i] == -1:  # Sell signal
                    self.exit_trade_safe(data, i, 'long')
        except Exception as e:
            print(f"Trade execution failed: {e}")

    def enter_trade_safe(self, data, index, order_type):
        """안전한 포지션 진입"""
        try:
            if self.equity is None or index >= len(data):
                return
                
            current_price = data['Close'].iloc[index]
            date = data.index[index]
            
            cash_available = self.equity.iloc[index-1]['cash'] if index > 0 else self.initial_capital

            if order_type == 'long' and cash_available > 0:
                order_size = min(cash_available / current_price, 0.1)  # 최대 0.1 단위
                cost = order_size * current_price * (1 + self.commission_rate)
                
                if cost <= cash_available:
                    self.trades.append({
                        'date': date, 
                        'type': 'buy', 
                        'price': current_price, 
                        'size': order_size
                    })
                    
                    self.equity.loc[date, 'holdings'] = order_size
                    self.equity.loc[date, 'cash'] = cash_available - cost

        except Exception as e:
            print(f"Enter trade failed: {e}")

    def exit_trade_safe(self, data, index, order_type):
        """안전한 포지션 종료"""
        try:
            if self.equity is None or index >= len(data):
                return
                
            current_price = data['Close'].iloc[index]
            date = data.index[index]
            
            holdings_available = self.equity.iloc[index-1]['holdings'] if index > 0 else 0

            if order_type == 'long' and holdings_available > 0:
                order_size = holdings_available
                revenue = order_size * current_price * (1 - self.commission_rate)
                
                self.trades.append({
                    'date': date, 
                    'type': 'sell', 
                    'price': current_price, 
                    'size': order_size
                })
                
                cash_before = self.equity.iloc[index-1]['cash'] if index > 0 else 0
                self.equity.loc[date, 'holdings'] = 0
                self.equity.loc[date, 'cash'] = cash_before + revenue

        except Exception as e:
            print(f"Exit trade failed: {e}")

    def calculate_equity_safe(self, data):
        """안전한 자산 곡선 계산"""
        try:
            if self.equity is None:
                return
                
            for i, date in enumerate(data.index):
                current_price = data['Close'].iloc[i]

                if i == 0:
                    self.equity.loc[date, 'holdings'] = 0.0
                    self.equity.loc[date, 'cash'] = float(self.initial_capital)
                else:
                    # 이전 값이 없으면 기본값 사용
                    if pd.isna(self.equity.loc[date, 'holdings']):
                        self.equity.loc[date, 'holdings'] = self.equity.iloc[i-1]['holdings']
                    if pd.isna(self.equity.loc[date, 'cash']):
                        self.equity.loc[date, 'cash'] = self.equity.iloc[i-1]['cash']

                # 총 자산 계산
                holdings_value = self.equity.loc[date, 'holdings'] * current_price
                cash_value = self.equity.loc[date, 'cash']
                self.equity.loc[date, 'total'] = holdings_value + cash_value

            # 수익률 계산
            self.equity['returns'] = self.equity['total'].pct_change().fillna(0)

        except Exception as e:
            print(f"Equity calculation failed: {e}")

    def get_performance(self):
        """성과 분석 - 타입 안전성 강화"""
        try:
            if hasattr(self, 'equity') and self.equity is not None and not self.equity.empty:
                # 히스토리컬 백테스팅 결과
                final_value = float(self.equity['total'].iloc[-1])
                return {
                    'initial_capital': float(self.initial_capital),
                    'final_value': final_value,
                    'total_trades': len(self.trades),
                    'profit_loss': final_value - float(self.initial_capital),
                    'returns': self.equity['returns'].tolist()
                }
            else:
                # 실시간 거래 결과
                total_holdings_value = 0.0
                default_prices = {"BTC": 45000.0, "ETH": 3000.0, "SOL": 150.0, "position": 45000.0}
                
                for asset, quantity in self.holdings.items():
                    try:
                        if quantity is None or quantity == 0:
                            continue
                        
                        # 타입 검증 및 변환
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

        except Exception as e:
            print(f"Performance calculation failed: {e}")
            return {
                'initial_capital': float(self.initial_capital),
                'final_balance': 0.0,
                'holdings_value': 0.0,
                'total_value': 0.0,
                'total_trades': 0,
                'profit_loss': -float(self.initial_capital)
            }

# 하위 호환성을 위한 별칭
AggressiveBacktester = SpotBacktester
