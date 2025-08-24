
import requests
import time
from typing import Dict, Any, Optional

class FuturesMCPClient:
    """Futures MCP API 클라이언트"""
    
    def __init__(self, api_key: str = "test_api_key", api_secret: str = "test_api_secret", base_url: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url or "https://api.example.com"
        self.session = requests.Session()
        
        # 시뮬레이션용 더미 데이터
        self.positions = {}
        self.balance = {"available": 10000.0, "total": 10000.0}
        self.market_prices = {
            "BTC/USDT": 45000,
            "ETH/USDT": 3000,
            "BTC-PERPETUAL": 45000
        }
        
    def execute_buy_order(self, symbol: str, amount: float) -> bool:
        """매수 주문 실행"""
        try:
            print(f"🟢 매수 주문 실행: {symbol}, 수량: {amount}")
            
            # 잔액 확인
            required_amount = amount * self.market_prices.get(symbol, 45000)
            if self.balance["available"] < required_amount:
                print(f"❌ 잔액 부족: 필요 ${required_amount}, 보유 ${self.balance['available']}")
                return False
            
            # 포지션 업데이트
            current_position = self.positions.get(symbol, 0)
            self.positions[symbol] = current_position + amount
            
            # 잔액 업데이트
            self.balance["available"] -= required_amount
            
            print(f"✅ 매수 완료: {symbol} {amount} @ ${self.market_prices.get(symbol, 45000)}")
            return True
            
        except Exception as e:
            print(f"❌ 매수 주문 실패: {e}")
            return False
    
    def execute_sell_order(self, symbol: str, amount: float) -> bool:
        """매도 주문 실행"""
        try:
            print(f"🔴 매도 주문 실행: {symbol}, 수량: {amount}")
            
            # 포지션 확인
            current_position = self.positions.get(symbol, 0)
            if current_position < amount:
                print(f"❌ 포지션 부족: 필요 {amount}, 보유 {current_position}")
                return False
            
            # 포지션 업데이트
            self.positions[symbol] = current_position - amount
            
            # 잔액 업데이트
            revenue = amount * self.market_prices.get(symbol, 45000)
            self.balance["available"] += revenue
            
            print(f"✅ 매도 완료: {symbol} {amount} @ ${self.market_prices.get(symbol, 45000)}")
            return True
            
        except Exception as e:
            print(f"❌ 매도 주문 실패: {e}")
            return False
    
    def get_position(self, symbol: str) -> Dict[str, Any]:
        """포지션 조회"""
        position_size = self.positions.get(symbol, 0)
        return {
            "symbol": symbol,
            "size": position_size,
            "avg_entry_price": self.market_prices.get(symbol, 45000),
            "unrealized_pnl": 0,
            "side": "long" if position_size > 0 else "short" if position_size < 0 else "none"
        }
    
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """시장 데이터 조회"""
        # 시뮬레이션용 가격 변동
        import random
        base_price = self.market_prices.get(symbol, 45000)
        price_variation = random.uniform(-0.02, 0.02)  # ±2% 변동
        current_price = base_price * (1 + price_variation)
        
        self.market_prices[symbol] = current_price  # 업데이트
        
        return {
            "symbol": symbol,
            "price": current_price,
            "volume": random.randint(500000, 2000000),
            "high_24h": current_price * 1.05,
            "low_24h": current_price * 0.95,
            "change_24h": random.uniform(-5, 5)
        }
    
    def get_account_balance(self) -> Dict[str, float]:
        """계정 잔액 조회"""
        # 포지션 평가액 계산
        position_value = sum(
            size * self.market_prices.get(symbol, 45000) 
            for symbol, size in self.positions.items()
        )
        
        self.balance["total"] = self.balance["available"] + position_value
        return self.balance
    
    def get_futures_price(self, symbol: str) -> float:
        """선물 가격 조회"""
        market_data = self.get_market_data(symbol)
        return market_data["price"]
    
    def fetch_futures_price(self, symbol: str) -> float:
        """선물 가격 조회 (별칭)"""
        return self.get_futures_price(symbol)
    
    def get_futures_position(self, symbol: str) -> Dict[str, Any]:
        """선물 포지션 조회 (별칭)"""
        return self.get_position(symbol)

# 하위 호환성을 위한 클래스들
class SpotMCPClient(FuturesMCPClient):
    """현물 MCP 클라이언트 (Futures 클라이언트 상속)"""
    
    def fetch_spot_price(self, symbol: str) -> float:
        """현물 가격 조회"""
        return self.get_futures_price(symbol)
    
    def get_spot_position(self, symbol: str) -> Dict[str, Any]:
        """현물 포지션 조회"""
        return self.get_position(symbol)

class SpotMarketData:
    """현물 시장 데이터"""
    
    def __init__(self, api_url: str):
        self.api_url = api_url
    
    def get_price(self, symbol: str) -> float:
        """시장 가격 조회"""
        # 더미 구현
        return 45000.0

class FuturesTradingStrategy:
    """선물 거래 전략"""
    
    def __init__(self, client: FuturesMCPClient, market_data):
        self.client = client
        self.market_data = market_data
    
    def execute_moving_average_strategy(self, symbol: str, short_window: int = 10, long_window: int = 30):
        """이동평균 전략 실행"""
        print(f"이동평균 전략 실행: {symbol} (단기: {short_window}, 장기: {long_window})")
        # 더미 구현
        return True

class SpotTradingStrategy:
    """현물 거래 전략"""
    
    def __init__(self, client: SpotMCPClient, market_data):
        self.client = client
        self.market_data = market_data
    
    def execute_rsi_strategy(self, symbol: str, window: int = 14, overbought: int = 70, oversold: int = 30):
        """RSI 전략 실행"""
        print(f"RSI 전략 실행: {symbol} (윈도우: {window}, 과매수: {overbought}, 과매도: {oversold})")
        # 더미 구현
        return True

if __name__ == "__main__":
    # Example Usage
    futures_client = FuturesMCPClient("futures_api_key", "futures_api_secret")
    futures_strategy = FuturesTradingStrategy(futures_client, None)

    btc_futures_symbol = "BTC-USD-230929"
    print(f"\n--- Futures Operations for {btc_futures_symbol} ---")
    futures_price = futures_client.fetch_futures_price(btc_futures_symbol)
    print(f"Current futures price: {futures_price}")

    futures_position = futures_client.get_futures_position(btc_futures_symbol)
    print(f"Futures position: {futures_position}")

    futures_strategy.execute_moving_average_strategy(btc_futures_symbol, short_window=10, long_window=30)

    # Example Usage for Spot
    spot_client = SpotMCPClient("spot_api_key", "spot_api_secret")
    spot_data = SpotMarketData("https://spot.api.example.com")
    spot_strategy = SpotTradingStrategy(spot_client, spot_data)

    eth_spot_symbol = "ETH-USD"
    print(f"\n--- Spot Operations for {eth_spot_symbol} ---")
    spot_price = spot_client.fetch_spot_price(eth_spot_symbol)
    print(f"Current spot price: {spot_price}")

    spot_position = spot_client.get_spot_position(eth_spot_symbol)
    print(f"Spot position: {spot_position}")

    spot_strategy.execute_rsi_strategy(eth_spot_symbol, window=14, overbought=70, oversold=30)
