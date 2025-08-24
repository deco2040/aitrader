
#!/usr/bin/env python3
"""
Futures 백테스팅 시스템
"""

from datetime import datetime
from typing import List, Dict, Any

class FuturesBacktester:
    def __init__(self, initial_capital: float, commission_rate: float):
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.balance = initial_capital
        self.position = 0
        self.trades = []
        self.equity_curve = []
        self.max_drawdown = 0
        self.peak_balance = initial_capital

    def buy(self, price: float, quantity: float) -> bool:
        """매수 실행"""
        # 입력 값 검증
        if price <= 0 or quantity <= 0:
            print(f"❌ 잘못된 입력값: price={price}, quantity={quantity}")
            return False

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
            print(f"✅ Buy: {quantity} at ${price}")
            return True
        else:
            print(f"❌ 잔액 부족: 필요 ${cost:.2f}, 보유 ${self.balance:.2f}")
            return False

    def sell(self, price: float, quantity: float) -> bool:
        """매도 실행"""
        # 입력 값 검증
        if price <= 0 or quantity <= 0:
            print(f"❌ 잘못된 입력값: price={price}, quantity={quantity}")
            return False

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
            print(f"✅ Sell: {quantity} at ${price}")
            return True
        else:
            print(f"❌ 포지션 부족: 요청 {quantity}, 보유 {self.position}")
            return False

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

    def get_performance(self) -> Dict[str, Any]:
        """성과 분석 - 타입 안전성 강화"""
        try:
            # 안전한 타입 변환
            balance_safe = float(self.balance) if self.balance is not None else 0.0
            position_safe = float(self.position) if self.position is not None else 0.0
            initial_capital_safe = float(self.initial_capital)
            
            position_value = position_safe * 45000  # 현재가 가정
            total_value = balance_safe + position_value
            profit_loss = total_value - initial_capital_safe
            roi = (profit_loss / initial_capital_safe) * 100 if initial_capital_safe > 0 else 0

            # 안전한 거래 분석
            winning_trades = []
            losing_trades = []
            total_commission = 0.0
            
            for t in self.trades:
                try:
                    if t['type'] == 'sell':
                        revenue = float(t.get('revenue', 0))
                        cost = float(t.get('cost', 0))
                        if revenue > cost:
                            winning_trades.append(t)
                        else:
                            losing_trades.append(t)
                    elif t['type'] == 'buy':
                        cost = float(t.get('cost', 0))
                        total_commission += cost * self.commission_rate
                except (ValueError, TypeError, KeyError):
                    continue

            return {
                'initial_capital': initial_capital_safe,
                'final_balance': balance_safe,
                'position_value': position_value,
                'total_value': total_value,
                'total_trades': len(self.trades),
                'profit_loss': profit_loss,
                'roi_percent': roi,
                'max_drawdown_percent': self.max_drawdown * 100,
                'winning_trades': len(winning_trades),
                'losing_trades': len(losing_trades),
                'total_commission_paid': total_commission
            }
        except Exception as e:
            print(f"Performance calculation error: {e}")
            # 기본값 반환
            return {
                'initial_capital': float(self.initial_capital),
                'final_balance': 0.0,
                'position_value': 0.0,
                'total_value': 0.0,
                'total_trades': 0,
                'profit_loss': -float(self.initial_capital),
                'roi_percent': -100.0,
                'max_drawdown_percent': 0.0,
                'winning_trades': 0,
                'losing_trades': 0,
                'total_commission_paid': 0.0
            }

    def generate_report(self) -> str:
        """상세 보고서 생성"""
        performance = self.get_performance()

        report = f"""
=== 백테스팅 성과 보고서 ===
초기 자본: ${performance['initial_capital']:,}
최종 잔액: ${performance['final_balance']:,}
포지션 가치: ${performance['position_value']:,}
총 자산: ${performance['total_value']:,}
손익: ${performance['profit_loss']:,}
수익률: {performance['roi_percent']:.2f}%
최대 손실폭: {performance['max_drawdown_percent']:.2f}%
총 거래 수: {performance['total_trades']}
승률: {performance['winning_trades']}/{performance['total_trades']}
"""
        return report
