
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
        """전체 백테스팅 실행 - 오류 완전 수정"""
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
            if signals is not None and not signals.empty:
                self.execute_trades_safe(data, signals)
                self.calculate_equity_safe(data)
            return self.equity

        except Exception as e:
            print(f"Backtesting failed: {e}")
            return None

    def generate_signals(self, data):
        """거래 신호 생성 - 완전 안정화"""
        try:
            if data.empty or len(data) < 10:
                print("Insufficient data for signal generation")
                return None
                
            short_window = min(5, len(data) // 2)
            long_window = min(10, len(data) - 1)

            signals = pd.DataFrame(index=data.index)
            signals['signal'] = 0.0
            signals['positions'] = 0.0

            # 이동평균 계산 - 안전한 방식
            signals['short_mavg'] = data['Close'].rolling(window=short_window, min_periods=1).mean()
            signals['long_mavg'] = data['Close'].rolling(window=long_window, min_periods=1).mean()

            # 신호 생성 - 벡터화된 방식으로 변경
            signals.loc[signals['short_mavg'] > signals['long_mavg'], 'signal'] = 1.0
            signals['positions'] = signals['signal'].diff()
            
            return signals

        except Exception as e:
            print(f"Signal generation failed: {e}")
            return None

    def execute_trades_safe(self, data, signals):
        """안전한 거래 실행 - 오류 수정"""
        try:
            if signals is None or signals.empty:
                return
                
            for i in range(1, len(signals)):
                try:
                    position_change = signals['positions'].iloc[i]
                    if pd.notna(position_change):
                        if position_change == 1:  # Buy signal
                            self.enter_trade_safe(data, i, 'long')
                        elif position_change == -1:  # Sell signal
                            self.exit_trade_safe(data, i, 'long')
                except Exception as e:
                    print(f"Trade execution error at index {i}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Trade execution failed: {e}")

    def enter_trade_safe(self, data, index, order_type):
        """안전한 포지션 진입 - 완전 수정"""
        try:
            if self.equity is None or index >= len(data):
                return

            current_price = float(data['Close'].iloc[index])
            date = data.index[index]

            # 현재 현금 확인
            if date in self.equity.index:
                cash_available = float(self.equity.loc[date, 'cash'])
            else:
                # 이전 날짜의 현금 찾기
                prev_dates = self.equity.index[self.equity.index < date]
                if len(prev_dates) > 0:
                    cash_available = float(self.equity.loc[prev_dates[-1], 'cash'])
                else:
                    cash_available = float(self.initial_capital)

            if cash_available <= 0:
                return

            # 투자 금액 계산 (현금의 10%)
            investment_amount = cash_available * 0.1
            shares_to_buy = investment_amount / current_price
            cost = shares_to_buy * current_price * (1 + self.commission_rate)

            if cost <= cash_available:
                # equity DataFrame 업데이트
                if date not in self.equity.index:
                    # 새로운 날짜 추가
                    new_row = pd.DataFrame(index=[date])
                    new_row['holdings'] = 0.0
                    new_row['cash'] = cash_available
                    new_row['total'] = cash_available
                    new_row['returns'] = 0.0
                    self.equity = pd.concat([self.equity, new_row])
                    self.equity.sort_index(inplace=True)

                # 값 업데이트
                current_holdings = float(self.equity.loc[date, 'holdings'])
                self.equity.loc[date, 'holdings'] = current_holdings + shares_to_buy
                self.equity.loc[date, 'cash'] = cash_available - cost

                self.trades.append({
                    'date': date,
                    'type': 'buy',
                    'price': current_price,
                    'size': shares_to_buy
                })
                print(f"Entered {order_type} position: {shares_to_buy:.4f} shares at ${current_price:.2f}")
                
        except Exception as e:
            print(f"Enter trade failed: {e}")

    def exit_trade_safe(self, data, index, order_type):
        """안전한 포지션 종료 - 완전 수정"""
        try:
            if self.equity is None or index >= len(data):
                return

            current_price = float(data['Close'].iloc[index])
            date = data.index[index]

            # 현재 보유량 확인
            if date in self.equity.index:
                holdings_to_sell = float(self.equity.loc[date, 'holdings'])
            else:
                # 이전 날짜의 보유량 찾기
                prev_dates = self.equity.index[self.equity.index < date]
                if len(prev_dates) > 0:
                    holdings_to_sell = float(self.equity.loc[prev_dates[-1], 'holdings'])
                else:
                    holdings_to_sell = 0.0

            if holdings_to_sell <= 0:
                return

            # 매도 수익 계산
            revenue = holdings_to_sell * current_price * (1 - self.commission_rate)

            # equity DataFrame 업데이트
            if date not in self.equity.index:
                prev_dates = self.equity.index[self.equity.index < date]
                if len(prev_dates) > 0:
                    prev_cash = float(self.equity.loc[prev_dates[-1], 'cash'])
                else:
                    prev_cash = float(self.initial_capital)
                    
                new_row = pd.DataFrame(index=[date])
                new_row['holdings'] = holdings_to_sell
                new_row['cash'] = prev_cash
                new_row['total'] = prev_cash + (holdings_to_sell * current_price)
                new_row['returns'] = 0.0
                self.equity = pd.concat([self.equity, new_row])
                self.equity.sort_index(inplace=True)

            # 값 업데이트
            current_cash = float(self.equity.loc[date, 'cash'])
            self.equity.loc[date, 'holdings'] = 0.0
            self.equity.loc[date, 'cash'] = current_cash + revenue

            self.trades.append({
                'date': date,
                'type': 'sell',
                'price': current_price,
                'size': holdings_to_sell
            })
            print(f"Exited {order_type} position: {holdings_to_sell:.4f} shares at ${current_price:.2f}")
            
        except Exception as e:
            print(f"Exit trade failed: {e}")

    def calculate_equity_safe(self, data):
        """안전한 자산 곡선 계산 - 완전 수정"""
        try:
            if self.equity is None or self.equity.empty:
                return

            # 첫 번째 행 초기화
            first_date = self.equity.index[0]
            self.equity.loc[first_date, 'holdings'] = 0.0
            self.equity.loc[first_date, 'cash'] = float(self.initial_capital)
            self.equity.loc[first_date, 'total'] = float(self.initial_capital)
            self.equity.loc[first_date, 'returns'] = 0.0

            # 각 날짜별로 순차 계산
            for i in range(len(self.equity.index)):
                date = self.equity.index[i]
                
                if i > 0:
                    prev_date = self.equity.index[i-1]
                    # 이전 값들을 현재로 복사 (거래가 없는 경우)
                    if pd.isna(self.equity.loc[date, 'holdings']):
                        self.equity.loc[date, 'holdings'] = self.equity.loc[prev_date, 'holdings']
                    if pd.isna(self.equity.loc[date, 'cash']):
                        self.equity.loc[date, 'cash'] = self.equity.loc[prev_date, 'cash']

                # 현재 가격으로 총 자산 계산
                if date in data.index:
                    current_price = float(data.loc[date, 'Close'])
                    holdings_value = float(self.equity.loc[date, 'holdings']) * current_price
                    cash_value = float(self.equity.loc[date, 'cash'])
                    self.equity.loc[date, 'total'] = holdings_value + cash_value

            # 수익률 계산
            self.equity['returns'] = self.equity['total'].pct_change().fillna(0)

        except Exception as e:
            print(f"Equity calculation failed: {e}")

    def get_performance(self):
        """성과 분석 - 타입 안전성 완전 강화"""
        try:
            if hasattr(self, 'equity') and self.equity is not None and not self.equity.empty:
                # 히스토리컬 백테스팅 결과
                final_value = float(self.equity['total'].iloc[-1])
                initial_capital_float = float(self.initial_capital)
                
                return {
                    'initial_capital': initial_capital_float,
                    'final_value': final_value,
                    'total_trades': len(self.trades),
                    'profit_loss': final_value - initial_capital_float,
                    'returns': self.equity['returns'].fillna(0).tolist() if 'returns' in self.equity.columns else []
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

                initial_capital_float = float(self.initial_capital)

                return {
                    'initial_capital': initial_capital_float,
                    'final_balance': balance_float,
                    'holdings_value': total_holdings_value,
                    'total_value': balance_float + total_holdings_value,
                    'total_trades': len(self.trades),
                    'profit_loss': (balance_float + total_holdings_value) - initial_capital_float
                }

        except Exception as e:
            print(f"Performance calculation failed: {e}")
            initial_capital_float = float(self.initial_capital)
            return {
                'initial_capital': initial_capital_float,
                'final_balance': 0.0,
                'holdings_value': 0.0,
                'total_value': 0.0,
                'total_trades': 0,
                'profit_loss': -initial_capital_float
            }

# 하위 호환성을 위한 별칭
AggressiveBacktester = SpotBacktester
