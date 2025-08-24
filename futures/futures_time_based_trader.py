try:
    from .futures_config import TIME_BASED_LEVERAGE, FEES, SCALPING_MODE, TRADING_HOURS
except ImportError:
    from futures_config import TIME_BASED_LEVERAGE, FEES, SCALPING_MODE, TRADING_HOURS

from datetime import datetime
from typing import Dict, Any

class TimeBasedTradingManager:
    """시간 기반 거래 관리자"""

    def __init__(self):
        self.current_time = datetime.utcnow()

    def get_trading_recommendation(self) -> Dict[str, Any]:
        """시간대별 거래 추천"""
        current_hour = self.current_time.hour

        is_high_volume = TRADING_HOURS["active_start"] <= current_hour <= TRADING_HOURS["active_end"]
        near_funding = any(abs(current_hour - ft) <= 1 for ft in TRADING_HOURS["funding_times"])

        leverage_multiplier = TIME_BASED_LEVERAGE["high_volume"] if is_high_volume else TIME_BASED_LEVERAGE["low_volume"]

        if near_funding:
            leverage_multiplier = TIME_BASED_LEVERAGE["funding_time"]

        return {
            "current_hour_utc": current_hour,
            "is_high_volume": is_high_volume,
            "near_funding": near_funding,
            "should_trade": is_high_volume and not near_funding,
            "leverage_multiplier": leverage_multiplier,
            "reason": self._get_trading_reason(is_high_volume, near_funding)
        }

    def _get_trading_reason(self, is_high_volume: bool, near_funding: bool) -> str:
        """거래 추천 이유"""
        if near_funding:
            return "펀딩 시간 근접으로 거래 자제 권장"
        elif is_high_volume:
            return "고거래량 시간대로 적극적 거래 권장"
        else:
            return "저거래량 시간대로 보수적 거래 권장"