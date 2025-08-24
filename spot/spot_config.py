
"""
현물 거래 설정 파일
"""

# 거래 설정
SPOT_TRADING_CONFIG = {
    "default_amount": 1000.0,
    "commission_rate": 0.001,
    "slippage_rate": 0.001,
    "max_position_size": 10000.0
}

# 지원 심볼
SUPPORTED_SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT", 
    "ADA/USDT",
    "SOL/USDT"
]

# 백테스팅 설정
BACKTEST_CONFIG = {
    "initial_capital": 10000,
    "commission_rate": 0.001,
    "start_date": "2023-01-01",
    "end_date": "2024-01-01"
}
