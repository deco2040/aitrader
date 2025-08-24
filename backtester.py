
#!/usr/bin/env python3
"""
🚀 통합 백테스팅 시스템
- Futures와 Spot 거래 모두 지원
- 간단하고 효율적인 구조
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd

class UnifiedBacktester:
    def __init__(self, initial_capital: float = 10000, commission_rate: float = 0.001):
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.balance = initial_capital
        self.positions = {}  # asset -> quantity
        self.trades = []
        
    def buy(self, asset: str, price: float, quantity: float) -> bool:
        """매수 주문"""
        if price <= 0 or quantity <= 0:
            return False
            
        cost = price * quantity * (1 + self.commission_rate)
        
        if self.balance >= cost:
            self.balance -= cost
            self.positions[asset] = self.positions.get(asset, 0) + quantity
            
            self.trades.append({
                'type': 'buy',
                'asset': asset,
                'price': price,
                'quantity': quantity,
                'cost': cost,
                'timestamp': datetime.now()
            })
            return True
        return False
    
    def sell(self, asset: str, price: float, quantity: float) -> bool:
        """매도 주문"""
        if price <= 0 or quantity <= 0:
            return False
            
        current_position = self.positions.get(asset, 0)
        if current_position >= quantity:
            revenue = price * quantity * (1 - self.commission_rate)
            self.balance += revenue
            self.positions[asset] -= quantity
            
            if self.positions[asset] == 0:
                del self.positions[asset]
            
            self.trades.append({
                'type': 'sell',
                'asset': asset,
                'price': price,
                'quantity': quantity,
                'revenue': revenue,
                'timestamp': datetime.now()
            })
            return True
        return False
    
    def get_performance(self) -> Dict[str, Any]:
        """성과 분석"""
        # 기본 가격 (실제로는 현재 시장가격을 사용해야 함)
        default_prices = {
            'BTC': 45000,
            'ETH': 3000,
            'SOL': 150,
            'position': 45000  # Futures용
        }
        
        position_value = sum(
            qty * default_prices.get(asset, 100) 
            for asset, qty in self.positions.items()
        )
        
        total_value = self.balance + position_value
        profit_loss = total_value - self.initial_capital
        roi = (profit_loss / self.initial_capital) * 100
        
        return {
            'initial_capital': self.initial_capital,
            'final_balance': self.balance,
            'position_value': position_value,
            'total_value': total_value,
            'profit_loss': profit_loss,
            'roi_percent': roi,
            'total_trades': len(self.trades)
        }
    
    def generate_report(self) -> str:
        """간단한 리포트 생성"""
        perf = self.get_performance()
        
        return f"""
=== 백테스팅 리포트 ===
초기 자본: ${perf['initial_capital']:,.2f}
최종 잔액: ${perf['final_balance']:,.2f}
포지션 가치: ${perf['position_value']:,.2f}
총 자산: ${perf['total_value']:,.2f}
손익: ${perf['profit_loss']:,.2f}
수익률: {perf['roi_percent']:.2f}%
총 거래: {perf['total_trades']}
"""

# 하위 호환성을 위한 별칭
FuturesBacktester = UnifiedBacktester
SpotBacktester = UnifiedBacktester
