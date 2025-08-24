class FuturesMCPClient:
    """
    Futures MCP Client for handling trading operations
    """

    def __init__(self, api_key=None, api_secret=None):
        self.api_key = api_key or "dummy_api_key"
        self.api_secret = api_secret or "dummy_api_secret"
        self.positions = {}
        self.balance = {"available": 10000.0, "total": 10000.0}
        self.market_prices = {"BTC/USDT": 45000.0}

    def execute_buy_order(self, symbol: str, amount: float) -> bool:
        """매수 주문 실행"""
        try:
            cost = amount * self.market_prices.get(symbol, 45000)
            if self.balance["available"] >= cost:
                self.balance["available"] -= cost
                current_pos = self.positions.get(symbol, {"size": 0, "avg_price": 0})

                # 포지션 업데이트
                total_size = current_pos["size"] + amount
                if total_size > 0:
                    avg_price = ((current_pos["size"] * current_pos["avg_price"]) +
                               (amount * self.market_prices.get(symbol, 45000))) / total_size
                else:
                    avg_price = self.market_prices.get(symbol, 45000)

                self.positions[symbol] = {"size": total_size, "avg_price": avg_price}
                print(f"✅ 매수 성공: {symbol} {amount} @ ${self.market_prices.get(symbol, 45000)}")
                return True
            else:
                print(f"❌ 잔액 부족: 필요 ${cost}, 보유 ${self.balance['available']}")
                return False
        except Exception as e:
            print(f"❌ 매수 주문 실패: {e}")
            return False

    def execute_sell_order(self, symbol: str, amount: float) -> bool:
        """매도 주문 실행"""
        try:
            current_pos = self.positions.get(symbol, {"size": 0, "avg_price": 0})
            if current_pos["size"] >= amount:
                revenue = amount * self.market_prices.get(symbol, 45000)
                self.balance["available"] += revenue

                # 포지션 업데이트
                new_size = current_pos["size"] - amount
                self.positions[symbol] = {"size": new_size, "avg_price": current_pos["avg_price"]}

                if new_size == 0:
                    del self.positions[symbol]

                print(f"✅ 매도 성공: {symbol} {amount} @ ${self.market_prices.get(symbol, 45000)}")
                return True
            else:
                print(f"❌ 포지션 부족: 필요 {amount}, 보유 {current_pos['size']}")
                return False
        except Exception as e:
            print(f"❌ 매도 주문 실패: {e}")
            return False

    def get_position(self, symbol: str) -> dict:
        """포지션 조회"""
        pos = self.positions.get(symbol, {"size": 0, "avg_price": 0})
        return {
            "symbol": symbol,
            "size": pos["size"],
            "avg_entry_price": pos["avg_price"],
            "unrealized_pnl": (self.market_prices.get(symbol, 45000) - pos["avg_price"]) * pos["size"]
        }

    def get_market_data(self, symbol: str) -> dict:
        """시장 데이터 조회"""
        return {
            "symbol": symbol,
            "price": self.market_prices.get(symbol, 45000),
            "volume": 1000000,
            "bid": self.market_prices.get(symbol, 45000) - 0.5,
            "ask": self.market_prices.get(symbol, 45000) + 0.5,
            "24h_change": 2.5
        }

    def get_account_balance(self) -> dict:
        """계정 잔액 조회"""
        total_position_value = sum(
            pos["size"] * self.market_prices.get(symbol, 45000)
            for symbol, pos in self.positions.items()
        )
        return {
            "available": self.balance["available"],
            "total": self.balance["available"] + total_position_value,
            "unrealized_pnl": sum(
                (self.market_prices.get(symbol, 45000) - pos["avg_price"]) * pos["size"]
                for symbol, pos in self.positions.items()
            )
        }

    def update_market_price(self, symbol: str, price: float):
        """시장 가격 업데이트 (테스트용)"""
        self.market_prices[symbol] = price