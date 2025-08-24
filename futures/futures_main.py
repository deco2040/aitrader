from futures.futures_claude_client import FuturesClaudeClient
from futures.futures_mcp_client import FuturesMCPClient
from futures.futures_time_based_trader import TimeBasedTradingManager
from futures.claude_enhanced_trader import ClaudeEnhancedTrader
from futures.futures_config import *
import time

class FuturesTrader:
    def __init__(self, claude_client: FuturesClaudeClient, mcp_client: FuturesMCPClient, claude_api_key: str = None):
        self.claude_client = claude_client
        self.mcp_client = mcp_client
        self.time_manager = TimeBasedTradingManager()
        
        # Claude Enhanced Trader 추가 (차별화된 AI 분석)
        if claude_api_key:
            self.enhanced_trader = ClaudeEnhancedTrader(claude_api_key, mcp_client)
        else:
            self.enhanced_trader = None

    def execute_futures_trading_strategy(self, symbol: str, amount: float) -> bool:
        """
        Futures 거래 전략을 실행합니다.

        Args:
            symbol (str): 거래할 금융 상품 심볼 (예: 'BTC-PERPETUAL').
            amount (float): 거래할 금액.

        Returns:
            bool: 거래 성공 여부.
        """
        try:
            # 시간대 기반 거래 검증
            trading_recommendation = self.time_manager.get_trading_recommendation()
            print(f"Trading recommendation: {trading_recommendation}")
            
            if not trading_recommendation['should_trade']:
                print(f"Trading avoided: {trading_recommendation['reason']}")
                return False
            
            # 시간대에 따른 포지션 크기 조정
            adjusted_amount = self.time_manager.get_optimal_position_size(amount)
            print(f"Original amount: {amount}, Adjusted amount: {adjusted_amount}")
            amount = adjusted_amount
            # Claude API를 사용하여 거래 신호 생성
            signal = self.claude_client.generate_trading_signal(symbol=symbol, amount=amount)
            print(f"Generated signal for {symbol}: {signal}")

            # MCP API를 사용하여 거래 실행
            if signal == "BUY":
                success = self.mcp_client.execute_buy_order(symbol=symbol, amount=amount)
                print(f"Executed BUY order for {symbol} with amount {amount}. Success: {success}")
            elif signal == "SELL":
                success = self.mcp_client.execute_sell_order(symbol=symbol, amount=amount)
                print(f"Executed SELL order for {symbol} with amount {amount}. Success: {success}")
            else:
                print(f"No trading action for {symbol} based on signal: {signal}")
                return False

            return success
        except Exception as e:
            print(f"An error occurred during futures trading for {symbol}: {e}")
            return False

    def execute_intelligent_trading_strategy(self, symbol: str) -> dict:
        """
        🧠 Claude Sonnet 4 기반 지능형 거래 전략 (차별화 포인트!)
        - 뉴스/소셜 감정 분석
        - 거시경제 맥락 이해  
        - 숨겨진 패턴 발견
        - 스토리텔링 기반 시장 해석
        """
        if not self.enhanced_trader:
            print("❌ Claude Enhanced Trader가 설정되지 않았습니다.")
            return {"success": False, "error": "Enhanced trader not available"}
        
        print(f"🚀 Claude 지능형 분석 시작: {symbol}")
        
        try:
            # Claude의 고급 분석 실행
            result = self.enhanced_trader.execute_intelligent_trade(symbol)
            
            print(f"✅ Claude 지능형 거래 완료")
            print(f"📊 분석 결과: {result['claude_analysis']['action']}")
            print(f"🎯 신뢰도: {result['claude_analysis']['confidence']}%")
            
            return {
                "success": True,
                "analysis": result['claude_analysis'],
                "narrative": result['market_narrative'],
                "execution": result['execution_result']
            }
            
        except Exception as e:
            print(f"❌ Claude 지능형 거래 오류: {e}")
            return {"success": False, "error": str(e)}

    def get_market_intelligence_report(self, symbol: str) -> str:
        """
        Claude가 생성하는 시장 인텔리전스 보고서
        """
        if not self.enhanced_trader:
            return "Enhanced trader not available"
        
        try:
            narrative = self.enhanced_trader.get_market_narrative(symbol)
            signal = self.enhanced_trader.get_intelligent_trading_signal(symbol)
            
            report = f"""
=== 🧠 Claude 시장 인텔리전스 보고서 ===
심볼: {symbol}
시간: {time.strftime('%Y-%m-%d %H:%M:%S')}

📖 시장 해석:
{narrative}

📊 분석 결과:
- 추천 행동: {signal.get('action', 'N/A')}
- 신뢰도: {signal.get('confidence', 0)}%
- 포지션 크기: {signal.get('position_size', 0)}
- 근거: {signal.get('reasoning', 'N/A')}

⚠️ 위험 요인:
{', '.join(signal.get('risk_factors', []))}

🔮 대안 시나리오:
{', '.join(signal.get('alternative_scenarios', []))}
            """
            
            return report
            
        except Exception as e:
            return f"보고서 생성 오류: {e}"

    def get_futures_position(self, symbol: str):
        """
        현재 futures 포지션 정보를 조회합니다.

        Args:
            symbol (str): 포지션을 조회할 금융 상품 심볼.

        Returns:
            dict: 포지션 정보.
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

        Args:
            symbol (str): 분석할 금융 상품 심볼.

        Returns:
            dict: 시장 분석 결과.
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

        Args:
            symbol (str): 청산할 금융 상품 심볼.

        Returns:
            bool: 포지션 청산 성공 여부.
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

        Returns:
            dict: 계정 잔액 정보.
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
    # 실제 사용 시에는 설정 파일에서 API 키 등을 로드해야 합니다.
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
            self.balance["total"] = self.balance["available"] + sum(self.positions.values()) # Simplified total balance calculation
            return True

        def execute_sell_order(self, symbol: str, amount: float) -> bool:
            print(f"[DummyFuturesMCPClient] Executing SELL order for {symbol} with amount {amount}")
            current_size = self.positions.get(symbol, 0)
            self.positions[symbol] = current_size - amount
            self.balance["available"] += amount
            self.balance["total"] = self.balance["available"] + sum(self.positions.values()) # Simplified total balance calculation
            return True

        def get_position(self, symbol: str) -> dict:
            print(f"[DummyFuturesMCPClient] Getting position for {symbol}")
            size = self.positions.get(symbol, 0)
            return {"symbol": symbol, "size": size, "avg_entry_price": 100.0} # Dummy price

        def get_market_data(self, symbol: str) -> dict:
            print(f"[DummyFuturesMCPClient] Getting market data for {symbol}")
            return {"symbol": symbol, "price": 25000.0, "volume": 1000000.0} # Dummy data

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