
<old_str>s</old_str>
<new_str>#!/usr/bin/env python3
"""
🔌 Futures MCP (Market Connect Protocol) Client
- 실시간 시장 데이터 연결
- 거래 실행 인터페이스
- 포지션 관리
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

class FuturesMCPClient:
    """Futures 시장 연결 클라이언트"""
    
    def __init__(self, api_key: str = "test_api", secret_key: str = "test_secret"):
        self.api_key = api_key
        self.secret_key = secret_key
        self.connected = False
        self.positions = {}
        self.last_prices = {
            "BTC/USDT": 45000.0,
            "ETH/USDT": 3000.0,
            "SOL/USDT": 150.0
        }
    
    def connect(self) -> bool:
        """거래소 연결"""
        try:
            # 시뮬레이션된 연결
            self.connected = True
            print("✅ MCP 클라이언트 연결 성공")
            return True
        except Exception as e:
            print(f"❌ MCP 연결 실패: {e}")
            return False
    
    def disconnect(self) -> None:
        """연결 해제"""
        self.connected = False
        print("🔌 MCP 클라이언트 연결 해제")
    
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """시장 데이터 조회"""
        if not self.connected:
            self.connect()
        
        # 시뮬레이션된 시장 데이터
        base_price = self.last_prices.get(symbol, 100.0)
        
        # 가격 변동 시뮬레이션 (±2%)
        import random
        price_change = random.uniform(-0.02, 0.02)
        current_price = base_price * (1 + price_change)
        self.last_prices[symbol] = current_price
        
        return {
            "symbol": symbol,
            "price": current_price,
            "volume": random.uniform(1000, 10000),
            "bid": current_price * 0.999,
            "ask": current_price * 1.001,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_position(self, symbol: str) -> Dict[str, Any]:
        """포지션 조회"""
        position = self.positions.get(symbol, {
            "symbol": symbol,
            "size": 0.0,
            "side": "none",
            "entry_price": 0.0,
            "unrealized_pnl": 0.0
        })
        
        # 미실현 손익 계산
        if position["size"] > 0:
            current_price = self.get_market_data(symbol)["price"]
            if position["side"] == "long":
                position["unrealized_pnl"] = (current_price - position["entry_price"]) * position["size"]
            elif position["side"] == "short":
                position["unrealized_pnl"] = (position["entry_price"] - current_price) * position["size"]
        
        return position
    
    def place_order(self, symbol: str, side: str, size: float, order_type: str = "market") -> Dict[str, Any]:
        """주문 실행"""
        if not self.connected:
            self.connect()
        
        market_data = self.get_market_data(symbol)
        price = market_data["price"]
        
        order = {
            "order_id": f"order_{int(time.time())}",
            "symbol": symbol,
            "side": side,
            "size": size,
            "price": price,
            "type": order_type,
            "status": "filled",
            "timestamp": datetime.now().isoformat()
        }
        
        # 포지션 업데이트
        self._update_position(symbol, side, size, price)
        
        print(f"✅ 주문 실행: {side} {size} {symbol} @ ${price:.2f}")
        return order
    
    def _update_position(self, symbol: str, side: str, size: float, price: float) -> None:
        """포지션 업데이트"""
        if symbol not in self.positions:
            self.positions[symbol] = {
                "symbol": symbol,
                "size": 0.0,
                "side": "none",
                "entry_price": 0.0,
                "unrealized_pnl": 0.0
            }
        
        position = self.positions[symbol]
        
        if side == "buy":
            if position["side"] == "short":
                # 숏 포지션 청산
                if size >= position["size"]:
                    remaining = size - position["size"]
                    position["size"] = remaining
                    position["side"] = "long" if remaining > 0 else "none"
                    position["entry_price"] = price if remaining > 0 else 0.0
                else:
                    position["size"] -= size
            else:
                # 롱 포지션 추가
                if position["size"] > 0:
                    # 평균 진입가 계산
                    total_value = position["size"] * position["entry_price"] + size * price
                    position["size"] += size
                    position["entry_price"] = total_value / position["size"]
                else:
                    position["size"] = size
                    position["entry_price"] = price
                position["side"] = "long"
        
        elif side == "sell":
            if position["side"] == "long":
                # 롱 포지션 청산
                if size >= position["size"]:
                    remaining = size - position["size"]
                    position["size"] = remaining
                    position["side"] = "short" if remaining > 0 else "none"
                    position["entry_price"] = price if remaining > 0 else 0.0
                else:
                    position["size"] -= size
            else:
                # 숏 포지션 추가
                if position["size"] > 0:
                    # 평균 진입가 계산
                    total_value = position["size"] * position["entry_price"] + size * price
                    position["size"] += size
                    position["entry_price"] = total_value / position["size"]
                else:
                    position["size"] = size
                    position["entry_price"] = price
                position["side"] = "short"
    
    def get_balance(self) -> Dict[str, float]:
        """잔액 조회"""
        return {
            "USDT": 10000.0,
            "available": 9500.0,
            "locked": 500.0
        }
    
    def get_funding_rate(self, symbol: str) -> float:
        """펀딩 비율 조회"""
        # 시뮬레이션된 펀딩 비율
        import random
        return random.uniform(-0.001, 0.001)</new_str>
