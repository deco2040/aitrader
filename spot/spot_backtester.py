
#!/usr/bin/env python3
"""
📊 현물 거래 백테스터
- UnifiedBacktester를 상속하여 현물 거래 전용 기능 제공
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backtester import UnifiedBacktester
from datetime import datetime, timedelta
import pandas as pd

class SpotBacktester(UnifiedBacktester):
    """현물 거래 전용 백테스터"""
    
    def __init__(self, symbol: str, start_date: str, end_date: str, initial_capital: float = 10000):
        super().__init__(initial_capital)
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.price_data = []
        
    def generate_sample_data(self):
        """샘플 가격 데이터 생성"""
        start = datetime.strptime(self.start_date, '%Y-%m-%d')
        end = datetime.strptime(self.end_date, '%Y-%m-%d')
        
        current_price = 50000  # 시작 가격
        current_date = start
        
        while current_date <= end:
            # 간단한 랜덤 워크
            import random
            change = random.uniform(-0.05, 0.05)  # ±5% 변동
            current_price *= (1 + change)
            
            self.price_data.append({
                'date': current_date,
                'price': current_price,
                'volume': random.uniform(1000, 10000)
            })
            
            current_date += timedelta(days=1)
    
    def backtest(self) -> pd.DataFrame:
        """백테스팅 실행"""
        if not self.price_data:
            self.generate_sample_data()
        
        equity_curve = []
        
        for i, data in enumerate(self.price_data):
            # 간단한 이동평균 전략
            if i >= 5:  # 5일 이동평균
                recent_prices = [p['price'] for p in self.price_data[i-4:i+1]]
                ma5 = sum(recent_prices) / 5
                current_price = data['price']
                
                # 매수 신호: 현재가 > 5일 이동평균
                if current_price > ma5 and self.balance > current_price * 0.1:
                    self.buy(self.symbol, current_price, 0.1)
                
                # 매도 신호: 현재가 < 5일 이동평균
                elif current_price < ma5 and self.symbol in self.positions:
                    position_size = self.positions[self.symbol]
                    if position_size > 0:
                        self.sell(self.symbol, current_price, min(0.1, position_size))
            
            # 자산 가치 기록
            position_value = self.positions.get(self.symbol, 0) * data['price']
            total_value = self.balance + position_value
            
            equity_curve.append({
                'date': data['date'],
                'total_value': total_value,
                'price': data['price']
            })
        
        return pd.DataFrame(equity_curve)
    
    def get_performance(self) -> dict:
        """성능 분석 (확장)"""
        base_perf = super().get_performance()
        
        if self.price_data:
            # 샤프 비율, 최대 낙폭 등 추가 지표
            start_price = self.price_data[0]['price']
            end_price = self.price_data[-1]['price']
            buy_and_hold_return = (end_price - start_price) / start_price * 100
            
            base_perf.update({
                'start_date': self.start_date,
                'end_date': self.end_date,
                'symbol': self.symbol,
                'buy_and_hold_return': buy_and_hold_return,
                'strategy_vs_bnh': base_perf['roi_percent'] - buy_and_hold_return
            })
        
        return base_perf
