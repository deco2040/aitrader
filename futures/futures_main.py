from datetime import datetime
from .futures_claude_client import FuturesClaudeClient
from .futures_mcp_client import FuturesMCPClient
from .futures_time_based_trader import TimeBasedTradingManager
from .claude_enhanced_trader import ClaudeEnhancedTrader
from .futures_config import *
import time

class FuturesTrader:
    """
    Main futures trading class that orchestrates all trading operations
    """

    def __init__(self, claude_client, mcp_client, claude_api_key=None):
        self.claude_client = claude_client
        self.mcp_client = mcp_client
        self.claude_api_key = claude_api_key
        self.time_manager = TimeBasedTradingManager()

        # Initialize Claude Enhanced Trader if API key provided
        if claude_api_key:
            try:
                self.enhanced_trader = ClaudeEnhancedTrader(claude_api_key, mcp_client)
            except Exception as e:
                print(f"Warning: Could not initialize ClaudeEnhancedTrader: {e}")
                self.enhanced_trader = None
        else:
            self.enhanced_trader = None

    def execute_futures_trading_strategy(self, symbol: str, amount: float) -> dict:
        """
        Execute basic futures trading strategy
        """
        try:
            # Get current market data
            market_data = self.mcp_client.get_market_data(symbol)
            current_position = self.mcp_client.get_position(symbol)

            # Get time-based trading recommendation
            recommendation = self.time_manager.get_trading_recommendation()

            print(f"Market data: {market_data}")
            print(f"Trading recommendation: {recommendation}")

            if not recommendation['should_trade']:
                return {
                    'success': True,
                    'action': 'HOLD',
                    'reason': recommendation['reason']
                }

            # Adjust amount based on time
            adjusted_amount = self.time_manager.get_optimal_position_size(amount)

            # Basic trading logic
            signal = self.claude_client.generate_trading_signal(symbol, adjusted_amount)

            if signal == "BUY" and current_position.get('size', 0) <= 0:
                success = self.mcp_client.execute_buy_order(symbol, adjusted_amount)
                return {'success': success, 'action': 'BUY', 'amount': adjusted_amount}
            elif signal == "SELL" and current_position.get('size', 0) > 0:
                success = self.mcp_client.execute_sell_order(symbol, adjusted_amount)
                return {'success': success, 'action': 'SELL', 'amount': adjusted_amount}
            else:
                return {'success': True, 'action': 'HOLD', 'reason': 'No trading signal'}

        except Exception as e:
            print(f"Error in execute_futures_trading_strategy: {e}")
            return {'success': False, 'error': str(e)}

    def execute_intelligent_trading_strategy(self, symbol: str) -> dict:
        """
        Execute Claude enhanced intelligent trading strategy
        """
        if not self.enhanced_trader:
            return {
                'success': False,
                'error': 'Claude Enhanced Trader not available'
            }

        try:
            # Use Claude enhanced analysis
            result = self.enhanced_trader.execute_intelligent_trade(symbol)
            return {
                'success': True,
                'analysis': result['claude_analysis'],
                'narrative': result['market_narrative'],
                'execution': result['execution_result']
            }
        except Exception as e:
            print(f"Error in execute_intelligent_trading_strategy: {e}")
            return {'success': False, 'error': str(e)}

    def get_market_intelligence_report(self, symbol: str) -> str:
        """
        Generate market intelligence report
        """
        try:
            market_data = self.mcp_client.get_market_data(symbol)
            position = self.mcp_client.get_position(symbol)
            balance = self.mcp_client.get_account_balance()
            recommendation = self.time_manager.get_trading_recommendation()

            report = f"""
🧠 Claude 시장 인텔리전스 보고서
================================
📊 심볼: {symbol}
💰 현재가: ${market_data.get('price', 'N/A')}
📈 거래량: {market_data.get('volume', 'N/A')}
🎯 포지션: {position.get('size', 0)}
💵 계정잔액: ${balance.get('available', 'N/A')}

⏰ 시간대 분석:
- 현재 UTC 시간: {recommendation['current_hour_utc']}시
- 고거래량 시간대: {'예' if recommendation['is_high_volume'] else '아니오'}
- 펀딩 시간 근접: {'예' if recommendation['near_funding'] else '아니오'}
- 거래 권장: {'예' if recommendation['should_trade'] else '아니오'}
- 추천 이유: {recommendation['reason']}

🔍 AI 분석 결과:
- 레버리지 배수: {recommendation['leverage_multiplier']}x
- 시장 상황: {'활발' if recommendation['is_high_volume'] else '조용'}
"""

            # Enhanced trader analysis if available
            if self.enhanced_trader:
                signal = self.enhanced_trader.get_intelligent_trading_signal(symbol)
                report += f"""
🎯 Claude 거래 신호:
- 추천 행동: {signal.get('action', 'N/A')}
- 신뢰도: {signal.get('confidence', 0)}%
- 근거: {signal.get('reasoning', 'N/A')}
"""

            return report

        except Exception as e:
            return f"보고서 생성 중 오류: {str(e)}"

    def get_futures_position(self, symbol: str):
        """
        현재 futures 포지션 정보를 조회합니다.
        """
        try:
            position = self.mcp_client.get_position(symbol=symbol)
            print(f"Position for {symbol}: {position}")
            return position
        except Exception as e:
            print(f"An error occurred while getting futures position for {symbol}: {e}")
            return None

    def analyze_futures_market(self, symbol: str):
        """
        Futures 시장 데이터를 분석합니다.
        """
        try:
            market_data = self.mcp_client.get_market_data(symbol=symbol)
            analysis = self.claude_client.analyze_market_data(market_data=market_data)
            print(f"Market analysis for {symbol}: {analysis}")
            return analysis
        except Exception as e:
            print(f"An error occurred during futures market analysis for {symbol}: {e}")
            return None

    def close_futures_position(self, symbol: str):
        """
        Futures 포지션을 청산합니다.
        """
        try:
            current_position = self.get_futures_position(symbol=symbol)
            if current_position and current_position.get("size", 0) > 0:
                print(f"Closing futures position for {symbol}...")
                success = self.mcp_client.execute_sell_order(symbol=symbol, amount=current_position["size"])
                print(f"Closed position for {symbol}. Success: {success}")
                return success
            elif current_position and current_position.get("size", 0) < 0:
                print(f"Closing futures position for {symbol}...")
                success = self.mcp_client.execute_buy_order(symbol=symbol, amount=abs(current_position["size"]))
                print(f"Closed position for {symbol}. Success: {success}")
                return success
            else:
                print(f"No open futures position to close for {symbol}.")
                return False
        except Exception as e:
            print(f"An error occurred while closing futures position for {symbol}: {e}")
            return False

    def get_futures_account_balance(self):
        """
        Futures 계정 잔액 정보를 조회합니다.
        """
        try:
            balance = self.mcp_client.get_account_balance()
            print(f"Futures account balance: {balance}")
            return balance
        except Exception as e:
            print(f"An error occurred while getting futures account balance: {e}")
            return None

if __name__ == '__main__':
    # Futures 클라이언트 및 트레이더 인스턴스 생성 (예시)
    print("Initializing Futures Trader...")

    # Dummy clients for demonstration
    class DummyFuturesClaudeClient:
        def generate_trading_signal(self, symbol: str, amount: float) -> str:
            print(f"[DummyFuturesClaudeClient] Generating signal for {symbol} with amount {amount}")
            if amount > 1000:
                return "BUY"
            else:
                return "SELL"

        def analyze_market_data(self, market_data: dict) -> dict:
            print(f"[DummyFuturesClaudeClient] Analyzing market data: {market_data}")
            return {"sentiment": "positive", "recommendation": "HOLD"}

    class DummyFuturesMCPClient:
        def __init__(self):
            self.positions = {}
            self.balance = {"available": 10000.0, "total": 10000.0}

        def execute_buy_order(self, symbol: str, amount: float) -> bool:
            print(f"[DummyFuturesMCPClient] Executing BUY order for {symbol} with amount {amount}")
            current_size = self.positions.get(symbol, 0)
            self.positions[symbol] = current_size + amount
            self.balance["available"] -= amount
            self.balance["total"] = self.balance["available"] + sum(self.positions.values())
            return True

        def execute_sell_order(self, symbol: str, amount: float) -> bool:
            print(f"[DummyFuturesMCPClient] Executing SELL order for {symbol} with amount {amount}")
            current_size = self.positions.get(symbol, 0)
            self.positions[symbol] = current_size - amount
            self.balance["available"] += amount
            self.balance["total"] = self.balance["available"] + sum(self.positions.values())
            return True

        def get_position(self, symbol: str) -> dict:
            print(f"[DummyFuturesMCPClient] Getting position for {symbol}")
            size = self.positions.get(symbol, 0)
            return {"symbol": symbol, "size": size, "avg_entry_price": 100.0}

        def get_market_data(self, symbol: str) -> dict:
            print(f"[DummyFuturesMCPClient] Getting market data for {symbol}")
            return {"symbol": symbol, "price": 25000.0, "volume": 1000000.0}

        def get_account_balance(self) -> dict:
            print(f"[DummyFuturesMCPClient] Getting account balance")
            return self.balance

    # 클라이언트 및 트레이더 초기화
    claude_client = DummyFuturesClaudeClient()
    mcp_client = DummyFuturesMCPClient()
    trader = FuturesTrader(claude_client=claude_client, mcp_client=mcp_client)

    # 거래 시뮬레이션
    symbol_to_trade = "BTC-PERPETUAL"
    trade_amount = 1500.0

    print(f"\n--- Starting Futures Trading Simulation for {symbol_to_trade} ---")

    # 시장 분석
    analysis = trader.analyze_futures_market(symbol=symbol_to_trade)

    # 거래 실행
    trade_success = trader.execute_futures_trading_strategy(symbol=symbol_to_trade, amount=trade_amount)

    # 포지션 확인
    position = trader.get_futures_position(symbol=symbol_to_trade)

    # 계정 잔액 확인
    balance = trader.get_futures_account_balance()

    # 포지션 청산 (예시)
    print(f"\n--- Closing Futures Position for {symbol_to_trade} ---")
    close_success = trader.close_futures_position(symbol=symbol_to_trade)

    # 최종 잔액 확인
    final_balance = trader.get_futures_account_balance()

    print("\n--- Futures Trading Simulation Ended ---")