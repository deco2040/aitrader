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

    def get_current_utc_hour(self) -> int:
        """현재 UTC 시간 반환"""
        return datetime.utcnow().hour

    def is_high_volume_time(self) -> bool:
        """거래량이 많은 시간대인지 확인"""
        current_hour = self.get_current_utc_hour()
        return TRADING_HOURS["active_start"] <= current_hour <= TRADING_HOURS["active_end"]

    def is_low_volume_time(self) -> bool:
        """거래량이 적은 시간대인지 확인"""
        return not self.is_high_volume_time()

    def is_near_funding_time(self) -> bool:
        """펀딩 시간 근처인지 확인"""
        current_hour = self.get_current_utc_hour()
        return any(abs(current_hour - ft) <= 1 for ft in TRADING_HOURS["funding_times"])

    def should_avoid_trading(self) -> bool:
        """거래를 피해야 하는 시간인지 확인"""
        return self.is_near_funding_time()

    def get_leverage_multiplier(self) -> float:
        """현재 시간대에 맞는 레버리지 배수 반환"""
        if self.is_near_funding_time():
            return TIME_BASED_LEVERAGE["funding_time"]
        elif self.is_high_volume_time():
            return TIME_BASED_LEVERAGE["high_volume"]
        else:
            return TIME_BASED_LEVERAGE["low_volume"]

    def get_optimal_position_size(self, base_size: float) -> float:
        """최적 포지션 크기 계산"""
        multiplier = self.get_leverage_multiplier()
        return base_size * multiplier

    def get_trading_recommendation(self) -> Dict[str, Any]:
        """시간대별 거래 추천"""
        current_hour = self.get_current_utc_hour()
        is_high_volume = self.is_high_volume_time()
        near_funding = self.is_near_funding_time()
        leverage_multiplier = self.get_leverage_multiplier()

        return {
            "current_hour_utc": current_hour,
            "is_high_volume": is_high_volume,
            "near_funding": near_funding,
            "should_trade": is_high_volume and not near_funding,
            "leverage_multiplier": leverage_multiplier,
            "reason": self._get_trading_reason(is_high_volume, near_funding)
        }

    def _get_trading_reason(self, is_high_volume: bool, near_funding: bool) -> str:
        """거래 추천 사유 반환"""
        if near_funding:
            return "펀딩 시간 근처로 거래 비추천"
        elif is_high_volume:
            return "높은 거래량 시간대로 거래 추천"
        else:
            return "낮은 거래량 시간대로 신중한 거래 필요"
        """거래 추천 이유"""
        if near_funding:
            return "펀딩 시간 근접으로 거래 자제 권장"
        elif is_high_volume:
            return "고거래량 시간대로 적극적 거래 권장"
        else:
            return "저거래량 시간대로 보수적 거래 권장"