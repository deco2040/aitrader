
"""
선물 거래 설정 파일
"""

# 선물 거래 설정
FUTURES_TRADING_CONFIG = {
    "default_leverage": 10,
    "max_leverage": 50,
    "default_amount": 1000.0,
    "commission_rate": 0.0004,
    "funding_rate_hours": [0, 8, 16],  # UTC 기준
    "high_volume_hours": [7, 8, 9, 13, 14, 15, 21, 22, 23]  # UTC 기준
}

# 지원 선물 계약
SUPPORTED_FUTURES = [
    "BTC-PERPETUAL",
    "ETH-PERPETUAL",
    "BTC/USDT",
    "ETH/USDT"
]

# 리스크 관리 설정
RISK_MANAGEMENT = {
    "max_position_size": 50000.0,
    "stop_loss_percentage": 5.0,
    "take_profit_percentage": 10.0,
    "max_daily_loss": 1000.0
}

# 시간대별 거래 설정
TIME_BASED_CONFIG = {
    "asian_session": [0, 1, 2, 3, 4, 5, 6, 7, 8],
    "european_session": [8, 9, 10, 11, 12, 13, 14, 15],
    "american_session": [13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
}

# 시간대별 레버리지 설정 (누락된 부분 추가)
TIME_BASED_LEVERAGE = {
    "high_volume_hours": [7, 8, 9, 13, 14, 15, 21, 22, 23],
    "low_volume_hours": [0, 1, 2, 3, 4, 5, 6],
    "high_volume_leverage": 1.5,
    "low_volume_leverage": 0.8
}

# 수수료 및 펀딩 시간 설정 (누락된 부분 추가)
FEES = {
    "commission_rate": 0.0004,
    "funding_times": [0, 8, 16]  # UTC 기준
}

# 스캘핑 모드 설정 (누락된 부분 추가)
SCALPING_MODE = {
    "enabled": False,
    "min_profit_target": 0.5,
    "max_hold_time": 300  # 초
}
"""
Futures 거래 시스템 설정 파일
"""

# 거래 시간 설정 (UTC 기준)
FUNDING_HOURS = [0, 8, 16]  # 펀딩 시간
TRADING_HOURS = list(range(0, 24))  # 거래 가능 시간

# 백테스팅 설정
DEFAULT_INITIAL_CAPITAL = 10000
DEFAULT_COMMISSION_RATE = 0.001
DEFAULT_SLIPPAGE_RATE = 0.001

# API 설정
MAX_RETRY_ATTEMPTS = 3
REQUEST_TIMEOUT = 30

# 리스크 관리
MAX_POSITION_SIZE = 0.1  # 포트폴리오의 10%
STOP_LOSS_PERCENT = 0.05  # 5% 손절
TAKE_PROFIT_PERCENT = 0.1  # 10% 익절

# 거래 쌍 설정
SUPPORTED_SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT", 
    "SOL/USDT",
    "BNB/USDT"
]
