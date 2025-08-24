
from .spot_backtester import SpotBacktester
from .spot_config import *

class SpotTrader:
    """현물 거래 메인 클래스"""
    
    def __init__(self, claude_client=None, mcp_client=None):
        self.claude_client = claude_client
        self.mcp_client = mcp_client
        
    def execute_spot_trading_strategy(self, symbol: str, amount: float):
        """현물 거래 전략 실행"""
        try:
            if self.mcp_client:
                market_data = self.mcp_client.get_market_data(symbol)
                return {"success": True, "market_data": market_data}
            else:
                return {"success": False, "error": "MCP client not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    print("Spot Trading System initialized")
