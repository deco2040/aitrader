# config.py - 수수료 반영 현실적 설정
import os
from dotenv import load_dotenv

load_dotenv()

# 🎯 현실적 수익률 조정 (수수료 고려)
SYMBOL = "BTC/USDT"
POSITION_SIZE = 100  # 50→100 (수수료 희석 효과)
DAILY_TARGET = 0.008  # 0.5%→0.8% (수수료 0.15-0.2% 감안)
MAX_DAILY_LOSS = 0.08  # 8% (더 공격적)
MAX_DAILY_TRADES = 8   # 3→8 (기회 확대)

# ⏰ 더 적극적인 분석 간격
ANALYSIS_INTERVAL = 300   # 10분→5분
STRATEGY_INTERVAL = 1800  # 1시간→30분  
RISK_INTERVAL = 180       # 5분→3분

# 🧠 Claude AI 최적화 (비용은 유지)
CLAUDE_MODEL = "claude-sonnet-4-20250514"
MAX_RETRIES = 2
MIN_AI_INTERVAL = 3600    # 2시간→1시간 (기회 놓치지 않게)
EMERGENCY_THRESHOLD = 5   # 7%→5% (더 민감하게)

# 🎯 더 적극적인 매매 규칙
LOCAL_RULES = {
    'stop_loss': -3.5,      # -2%→-3.5% (여유 확대)
    'take_profit': 2.8,     # 4%→2.8% (빠른 익절)
    'panic_sell': -6.0,     # -5%→-6% 
    'oversold_buy': -8.0,   # -7%→-8%
    'overbought_sell': 6.0  # 8%→6%
}

# 🔥 AI 휴식 시스템 대폭 축소
NO_REST_MODE = True  # AI는 24시간 가동
HUMAN_OVERRIDE_ONLY = True  # 사람만 중단 가능

# 💰 수수료 최적화 전략
FEE_OPTIMIZATION = {
    'min_profit_threshold': 0.25,  # 0.25% 이상만 매매
    'large_position_threshold': 150,  # $150 이상은 분할매수
    'quick_scalp_mode': True,  # 빠른 스캘핑 허용
    'maker_order_priority': True  # 가능하면 지정가 우선
}

# 📊 스마트 트리거 (더 민감하게)
SMART_TRIGGERS = {
    'price_change_threshold': 3.0,    # 5%→3%
    'loss_threshold': 2.0,            # 3%→2%
    'profit_threshold': 2.5,          # 4%→2.5%
    'volatility_threshold': 8.0,      # 10%→8%
    'position_risk_threshold': 0.12   # 0.15→0.12
}

# 🎯 분할매수 최적화 (수수료 고려)
MAX_SPLITS = 4        # 6→4 (수수료 절약)
MIN_SPLIT_AMOUNT = 30 # 20→30 (수수료 비중 줄임)
SPLIT_AGGRESSIVENESS = 1.5  # 더 빠른 분할