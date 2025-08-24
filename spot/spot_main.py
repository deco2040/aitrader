from .spot_backtester import SpotBacktester
from .spot_config import *
from .spot_ai_trader import SpotAITrader
from .spot_claude_client import SpotClaudeClient
import time

class SpotTrader:
    """
    현물 거래 메인 클래스
    """

    def __init__(self):
        self.ai_trader = SpotAITrader()
        self.backtester = None

    def initialize_backtester(self, symbol=None, start_date=None, end_date=None, initial_capital=10000):
        """백테스터 초기화"""
        self.backtester = SpotBacktester(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital
        )
        return self.backtester

    def run_backtest(self, symbol="AAPL", start_date="2023-01-01", end_date="2023-12-31"):
        """백테스트 실행"""
        backtester = self.initialize_backtester(symbol, start_date, end_date)
        if backtester:
            results = backtester.backtest()
            performance = backtester.get_performance()
            return {"results": results, "performance": performance}
        return None

    def execute_spot_trade(self, symbol, action, amount):
        """현물 거래 실행"""
        try:
            print(f"현물 거래 실행: {symbol}, {action}, {amount}")
            # AI 트레이더를 통한 거래 실행
            order_details = {
                "symbol": symbol,
                "action": action,
                "amount": amount
            }
            self.ai_trader.execute_trade(order_details)
            return {"success": True, "message": "거래 실행 완료"}
        except Exception as e:
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    trader = SpotTrader()

    # 백테스트 예제
    print("현물 백테스트 실행 중...")
    backtest_results = trader.run_backtest()
    if backtest_results:
        print(f"백테스트 완료: {backtest_results['performance']}")

    # 거래 예제
    trade_result = trader.execute_spot_trade("AAPL", "BUY", 100)
    print(f"거래 결과: {trade_result}")