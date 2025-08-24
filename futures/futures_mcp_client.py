import random
import time
from datetime import datetime
from typing import Dict, Any

class FuturesMCPClient:
    """
    Futures 거래를 위한 MCP(Market Connection Protocol) 클라이언트
    실제 거래소 연결을 위한 더미 구현
    """

    def __init__(self, api_key: str = "dummy_api", api_secret: str = "dummy_secret"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.positions = {}
        self.balance = {"available": 10000.0, "total": 10000.0}
        print(f"FuturesMCPClient initialized with API key: {api_key[:10]}...")

    def execute_buy_order(self, symbol: str, amount: float) -> bool:
        """매수 주문 실행"""
        try:
            print(f"[FuturesMCPClient] 매수 주문 실행: {symbol}, 수량: {amount}")

            # 잔액 확인
            required_margin = amount * 0.1  # 10배 레버리지 가정
            if self.balance["available"] < required_margin:
                print(f"잔액 부족: 필요 {required_margin}, 보유 {self.balance['available']}")
                return False

            # 포지션 업데이트
            current_position = self.positions.get(symbol, 0)
            self.positions[symbol] = current_position + amount
            self.balance["available"] -= required_margin

            # 약간의 지연 시뮬레이션
            time.sleep(0.1)

            print(f"✅ 매수 완료: {symbol}, 포지션: {self.positions[symbol]}")
            return True

        except Exception as e:
            print(f"❌ 매수 주문 실패: {e}")
            return False

    def execute_sell_order(self, symbol: str, amount: float) -> bool:
        """매도 주문 실행"""
        try:
            print(f"[FuturesMCPClient] 매도 주문 실행: {symbol}, 수량: {amount}")

            # 포지션 확인
            current_position = self.positions.get(symbol, 0)
            if current_position < amount:
                print(f"포지션 부족: 필요 {amount}, 보유 {current_position}")
                return False

            # 포지션 업데이트
            self.positions[symbol] = current_position - amount
            if self.positions[symbol] == 0:
                del self.positions[symbol]

            # 수익 반영 (간단한 시뮬레이션)
            profit = amount * random.uniform(-0.02, 0.05)  # -2% ~ +5% 랜덤 수익
            self.balance["available"] += (amount * 0.1) + profit  # 마진 반환 + 수익

            # 약간의 지연 시뮬레이션
            time.sleep(0.1)

            print(f"✅ 매도 완료: {symbol}, 남은 포지션: {self.positions.get(symbol, 0)}")
            return True

        except Exception as e:
            print(f"❌ 매도 주문 실패: {e}")
            return False

    def get_position(self, symbol: str) -> Dict[str, Any]:
        """포지션 정보 조회"""
        try:
            size = self.positions.get(symbol, 0)
            avg_price = random.uniform(40000, 50000) if symbol.startswith("BTC") else random.uniform(2500, 3500)

            return {
                "symbol": symbol,
                "size": size,
                "avg_entry_price": avg_price,
                "unrealized_pnl": size * random.uniform(-100, 200),
                "margin_required": size * 0.1
            }
        except Exception as e:
            print(f"포지션 조회 오류: {e}")
            return {"symbol": symbol, "size": 0, "avg_entry_price": 0}

    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """시장 데이터 조회"""
        try:
            # 심볼에 따른 기본 가격 설정
            base_price = 45000 if symbol.startswith("BTC") else 3000
            current_price = base_price + random.uniform(-1000, 1000)

            return {
                "symbol": symbol,
                "price": current_price,
                "volume": random.randint(100000, 2000000),
                "high_24h": current_price * 1.05,
                "low_24h": current_price * 0.95,
                "change_24h": random.uniform(-0.05, 0.05),
                "timestamp": int(time.time())
            }
        except Exception as e:
            print(f"시장 데이터 조회 오류: {e}")
            return {"symbol": symbol, "price": 0, "volume": 0}

    def get_account_balance(self) -> Dict[str, float]:
        """계정 잔액 조회"""
        try:
            # 포지션 가치 계산
            total_position_value = 0
            for symbol, size in self.positions.items():
                market_data = self.get_market_data(symbol)
                total_position_value += size * market_data["price"] * 0.1  # 마진 기준

            self.balance["total"] = self.balance["available"] + total_position_value

            return {
                "available": self.balance["available"],
                "used_margin": total_position_value,
                "total": self.balance["total"],
                "unrealized_pnl": random.uniform(-500, 1000)
            }
        except Exception as e:
            print(f"잔액 조회 오류: {e}")
            return {"available": 0, "total": 0}

    def get_order_history(self, symbol: str = None) -> list:
        """주문 내역 조회"""
        # 더미 주문 내역
        orders = [
            {
                "id": f"order_{i}",
                "symbol": symbol or "BTC/USDT",
                "side": "buy" if i % 2 == 0 else "sell",
                "amount": random.uniform(0.01, 1.0),
                "price": random.uniform(40000, 50000),
                "status": "filled",
                "timestamp": int(time.time()) - (i * 3600)
            }
            for i in range(5)
        ]
        return orders