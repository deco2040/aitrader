
# config.py - 선물 마진 거래 전용 설정
import os
from dotenv import load_dotenv

load_dotenv()

# 🎯 선물 거래 기본 설정
SYMBOL = "BTC/USDT"
LEVERAGE = 10  # 10배 레버리지
POSITION_SIZE = 100  # USDT 기준
DAILY_TARGET = 0.012  # 1.2% (레버리지 고려)
MAX_DAILY_LOSS = 0.05  # 5% (청산 방지)
MAX_DAILY_TRADES = 12  # 더 활발한 거래

# ⏰ 분석 간격 (선물은 더 빈번)
ANALYSIS_INTERVAL = 180  # 3분
STRATEGY_INTERVAL = 900  # 15분
RISK_INTERVAL = 120  # 2분

# 🧠 Claude AI 설정
CLAUDE_MODEL = "claude-sonnet-4-20250514"
MAX_RETRIES = 2
MIN_AI_INTERVAL = 1800  # 30분
EMERGENCY_THRESHOLD = 3  # 3% (더 민감)

# 🎯 선물 거래 전용 규칙
FUTURES_RULES = {
    'stop_loss': -2.5,  # -2.5% (레버리지 고려)
    'take_profit': 3.0,  # 3% 
    'panic_sell': -4.0,  # -4% (청산 방지)
    'liquidation_buffer': -8.0,  # 청산가 버퍼
    'funding_aware': True,  # 펀딩 수수료 고려
    'max_leverage_usage': 0.8  # 최대 80%만 사용
}

# 💰 수수료 구조 (선물)
FEES = {
    'maker': 0.0002,  # 0.02%
    'taker': 0.0004,  # 0.04% 
    'funding_rate': 0.0001,  # 0.01% (8시간마다)
    'funding_times': [0, 8, 16]  # UTC 시간
}

# 📊 리스크 관리 (선물 특화)
RISK_MANAGEMENT = {
    'max_position_ratio': 0.8,  # 최대 포지션 비율
    'liquidation_warning': 0.15,  # 청산가 15% 접근시 경고
    'funding_cost_limit': 0.5,  # 일일 펀딩 비용 한도 (%)
    'margin_ratio_min': 0.2,  # 최소 마진 비율
    'position_size_scaling': True  # 변동성에 따른 포지션 조정
}

# 🔥 레버리지 전략
LEVERAGE_STRATEGY = {
    'conservative': 5,   # 안정적 상황
    'normal': 10,        # 일반 상황  
    'aggressive': 15,    # 공격적 상황
    'max_allowed': 20    # 최대 허용
}

# ⚡ 빠른 스캘핑 설정
SCALPING_MODE = {
    'enabled': True,
    'min_profit': 0.5,   # 0.5% 이상
    'max_hold_time': 1800,  # 30분 최대 보유
    'quick_exit_loss': -1.0,  # -1% 빠른 손절
    'funding_time_exit': True  # 펀딩 시간 전 종료
}

# 🕐 시간대별 레버리지 조정
TIME_BASED_LEVERAGE = {
    'high_volume_hours': [14, 15, 16, 17],  # UTC
    'high_volume_leverage': 1.2,  # 20% 증가
    'low_volume_hours': [0, 1, 2, 3, 4, 5],
    'low_volume_leverage': 0.8   # 20% 감소
}

# 🎯 포지션 관리
POSITION_MANAGEMENT = {
    'partial_close_profit': 2.0,  # 2% 수익시 50% 부분 청산
    'trailing_stop_activation': 1.5,  # 1.5% 수익시 트레일링 시작
    'trailing_stop_distance': 0.8,    # 0.8% 거리 유지
    'dca_enabled': False,  # 물타기 비활성화 (선물 위험)
    'hedging_enabled': False  # 헤징 비활성화
}
