
import sys
import os
from typing import Dict, Any, Optional

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from spot_backtester import SpotBacktester
from spot_claude_client import SpotClaudeClient

class SpotTrader:
    """Spot 거래 메인 클래스"""
    
    def __init__(self, claude_client: SpotClaudeClient):
        self.claude_client = claude_client
        print("SpotTrader initialized successfully")
    
    def execute_spot_trading_strategy(self, symbol: str, amount: float) -> Dict[str, Any]:
        """기본 현물 거래 전략 실행"""
        try:
            print(f"Executing spot trading strategy for {symbol} with amount {amount}")
            
            # 잔액 확인
            balance = self.claude_client.get_balance("USD")
            
            if balance < amount:
                return {"success": False, "error": "Insufficient balance"}
            
            # 주문 실행
            order = self.claude_client.place_order(symbol, amount/50000, 50000, "BUY")
            
            return {
                "success": True,
                "order": order,
                "balance": balance
            }
            
        except Exception as e:
            print(f"현물 거래 전략 실행 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def run_backtest(self, symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """백테스팅 실행"""
        try:
            backtester = SpotBacktester(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                initial_capital=10000
            )
            
            # 백테스팅 실행
            equity_curve = backtester.backtest()
            performance = backtester.get_performance()
            
            return {
                "success": True,
                "performance": performance,
                "equity_curve": equity_curve is not None
            }
            
        except Exception as e:
            print(f"백테스팅 실행 실패: {e}")
            return {"success": False, "error": str(e)}

def main():
    """메인 실행 함수"""
    try:
        # 클라이언트 초기화
        claude_client = SpotClaudeClient("demo_api_key")
        
        # Spot Trader 초기화
        trader = SpotTrader(claude_client)
        
        # 테스트 거래 실행
        result = trader.execute_spot_trading_strategy("BTC-USD", 1000)
        print(f"거래 결과: {result}")
        
        print("Spot 거래 시스템 실행 완료")
        
    except Exception as e:
        print(f"메인 실행 오류: {e}")

if __name__ == "__main__":
    main()
