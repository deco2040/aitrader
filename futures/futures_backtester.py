
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class FuturesBacktester:
    def __init__(self, initial_capital, commission_rate):
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.balance = initial_capital
        self.position = 0
        self.trades = []
        self.equity_curve = []
        self.max_drawdown = 0
        self.peak_balance = initial_capital

    def buy(self, price, quantity):
        cost = price * quantity * (1 + self.commission_rate)
        if self.balance >= cost:
            self.balance -= cost
            self.position += quantity
            self.trades.append({
                'type': 'buy', 
                'price': price, 
                'quantity': quantity, 
                'cost': cost,
                'timestamp': datetime.now(),
                'balance_after': self.balance
            })
            self._update_equity()
            print(f"Bought {quantity} at ${price}. Balance: ${self.balance:.2f}")
        else:
            print(f"Insufficient balance to buy. Required: ${cost:.2f}, Available: ${self.balance:.2f}")

    def sell(self, price, quantity):
        if self.position >= quantity:
            revenue = price * quantity * (1 - self.commission_rate)
            self.balance += revenue
            self.position -= quantity
            self.trades.append({
                'type': 'sell', 
                'price': price, 
                'quantity': quantity, 
                'revenue': revenue,
                'timestamp': datetime.now(),
                'balance_after': self.balance
            })
            self._update_equity()
            print(f"Sold {quantity} at ${price}. Balance: ${self.balance:.2f}")
        else:
            print(f"Insufficient position to sell. Required: {quantity}, Available: {self.position}")

    def _update_equity(self):
        """자산 곡선 업데이트"""
        current_total = self.balance + (self.position * 45000)  # 현재가 가정
        self.equity_curve.append({
            'timestamp': datetime.now(),
            'total_value': current_total,
            'cash': self.balance,
            'position_value': self.position * 45000
        })
        
        # 최대 손실폭 계산
        if current_total > self.peak_balance:
            self.peak_balance = current_total
        else:
            drawdown = (self.peak_balance - current_total) / self.peak_balance
            if drawdown > self.max_drawdown:
                self.max_drawdown = drawdown

    def get_performance(self):
        """성과 분석"""
        total_value = self.balance + (self.position * 45000)  # 현재가 가정
        profit_loss = total_value - self.initial_capital
        roi = (profit_loss / self.initial_capital) * 100
        
        winning_trades = [t for t in self.trades if t['type'] == 'sell' and 'revenue' in t]
        losing_trades = [t for t in self.trades if t['type'] == 'sell' and 'revenue' in t]
        
        return {
            'initial_capital': self.initial_capital,
            'final_balance': self.balance,
            'position_value': self.position * 45000,
            'total_value': total_value,
            'total_trades': len(self.trades),
            'profit_loss': profit_loss,
            'roi_percent': roi,
            'max_drawdown_percent': self.max_drawdown * 100,
            'winning_trades': len([t for t in winning_trades if t.get('revenue', 0) > t.get('cost', 0)]),
            'total_commission_paid': sum(t.get('cost', 0) * self.commission_rate for t in self.trades)
        }

    def generate_report(self):
        """상세 보고서 생성"""
        performance = self.get_performance()
        
        report = f"""
=== 백테스팅 성과 보고서 ===
초기 자본: ${performance['initial_capital']:,.2f}
최종 잔액: ${performance['final_balance']:,.2f}
포지션 가치: ${performance['position_value']:,.2f}
총 자산 가치: ${performance['total_value']:,.2f}
손익: ${performance['profit_loss']:,.2f}
수익률: {performance['roi_percent']:.2f}%
최대 손실폭: {performance['max_drawdown_percent']:.2f}%
총 거래 수: {performance['total_trades']}
승률: {performance['winning_trades']}/{len([t for t in self.trades if t['type'] == 'sell'])}
총 수수료: ${performance['total_commission_paid']:,.2f}
"""
        return report

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
            self.trades.append({
                'type': 'buy', 
                'asset': asset, 
                'price': price, 
                'quantity': quantity, 
                'cost': cost,
                'timestamp': datetime.now()
            })
            print(f"Bought {quantity} of {asset} at ${price}. Balance: ${self.balance:.2f}")
        else:
            print("Insufficient balance to buy.")

    def sell(self, asset, price, quantity):
        if asset in self.holdings and self.holdings[asset] >= quantity:
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
        else:
            print(f"Insufficient holdings of {asset} to sell.")

    def get_performance(self):
        total_holdings_value = sum(quantity * 45000 for quantity in self.holdings.values())  # 가정가
        return {
            'initial_capital': self.initial_capital,
            'final_balance': self.balance,
            'holdings_value': total_holdings_value,
            'total_value': self.balance + total_holdings_value,
            'total_trades': len(self.trades),
            'profit_loss': (self.balance + total_holdings_value) - self.initial_capital
        }
