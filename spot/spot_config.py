
"""
현물 거래 설정 파일
"""

# 현물 거래 기본 설정
SPOT_TRADING_CONFIG = {
    "default_amount": 1000.0,
    "commission_rate": 0.001,
    "slippage_rate": 0.001,
    "max_position_per_asset": 10000.0
}

# 지원 현물 심볼
SUPPORTED_SPOT_SYMBOLS = [
    "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA",
    "BTC-USD", "ETH-USD", "NVDA", "META"
]

# 리스크 관리
SPOT_RISK_MANAGEMENT = {
    "max_portfolio_value": 100000.0,
    "max_single_position": 20000.0,
    "stop_loss_percentage": 10.0,
    "take_profit_percentage": 20.0
}

# 백테스팅 설정
BACKTESTING_CONFIG = {
    "default_start_date": "2023-01-01",
    "default_end_date": "2023-12-31",
    "initial_capital": 10000.0,
    "benchmark_symbol": "SPY"
}
