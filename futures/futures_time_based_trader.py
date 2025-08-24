import datetime
from typing import Dict, List
from .futures_config import TIME_BASED_LEVERAGE, FEES, SCALPING_MODE

class TimeBasedTradingManager:
    def __init__(self):
        self.high_volume_hours = TIME_BASED_LEVERAGE['high_volume_hours']
        self.low_volume_hours = TIME_BASED_LEVERAGE['low_volume_hours']
        self.funding_times = FEES['funding_times']

    def get_current_utc_hour(self) -> int:
        """현재 UTC 시간을 반환"""
        return datetime.datetime.utcnow().hour

    def is_high_volume_time(self) -> bool:
        """현재가 거래량이 많은 시간대인지 확인"""
        current_hour = self.get_current_utc_hour()
        return current_hour in self.high_volume_hours

    def is_low_volume_time(self) -> bool:
        """현재가 거래량이 적은 시간대인지 확인"""
        current_hour = self.get_current_utc_hour()
        return current_hour in self.low_volume_hours

    def get_leverage_multiplier(self) -> float:
        """시간대에 따른 레버리지 배수 반환"""
        if self.is_high_volume_time():
            return TIME_BASED_LEVERAGE['high_volume_leverage']
        elif self.is_low_volume_time():
            return TIME_BASED_LEVERAGE['low_volume_leverage']
        else:
            return 1.0  # 기본값

    def is_near_funding_time(self, minutes_before: int = 30) -> bool:
        """펀딩 시간 근처인지 확인"""
        current_time = datetime.datetime.utcnow()
        current_hour = current_time.hour
        current_minute = current_time.minute

        for funding_hour in self.funding_times:
            # 펀딩 시간 전 30분 확인
            if current_hour == funding_hour and current_minute >= (60 - minutes_before):
                return True
            # 펀딩 시간 후 10분 확인
            elif current_hour == funding_hour and current_minute <= 10:
                return True
        return False

    def should_avoid_trading(self) -> bool:
        """거래를 피해야 하는 시간인지 확인"""
        return (self.is_low_volume_time() and 
                not SCALPING_MODE['enabled']) or self.is_near_funding_time()

    def get_optimal_position_size(self, base_size: float, market_volatility: float = 1.0) -> float:
        """시간대와 변동성을 고려한 최적 포지션 크기 계산"""
        leverage_multiplier = self.get_leverage_multiplier()
        volatility_adjustment = min(1.0, 1.0 / market_volatility) if market_volatility > 1.0 else 1.0

        # 거래량이 적은 시간대에는 포지션 크기 축소
        if self.is_low_volume_time():
            return base_size * leverage_multiplier * volatility_adjustment * 0.7
        else:
            return base_size * leverage_multiplier * volatility_adjustment

    def get_trading_recommendation(self) -> Dict[str, any]:
        """현재 시간대 기반 거래 추천"""
        current_hour = self.get_current_utc_hour()

        recommendation = {
            'should_trade': not self.should_avoid_trading(),
            'leverage_multiplier': self.get_leverage_multiplier(),
            'is_high_volume': self.is_high_volume_time(),
            'near_funding': self.is_near_funding_time(),
            'current_hour_utc': current_hour,
            'reason': ''
        }

        if self.is_near_funding_time():
            recommendation['reason'] = 'Funding time approaching - avoid new positions'
        elif self.is_high_volume_time():
            recommendation['reason'] = 'High volume hours - increase position size'
        elif self.is_low_volume_time():
            recommendation['reason'] = 'Low volume hours - reduce position size'
        else:
            recommendation['reason'] = 'Normal trading hours'

        return recommendation
import datetime
import pytz
from .futures_config import TIME_BASED_LEVERAGE, FEES, SCALPING_MODE

class TimeBasedTradingManager:
    """시간대 기반 거래 관리자"""
    
    def __init__(self):
        self.config = TIME_BASED_LEVERAGE
        self.fees = FEES
        
    def get_current_utc_hour(self) -> int:
        """현재 UTC 시간 반환"""
        return datetime.datetime.utcnow().hour
    
    def is_high_volume_time(self) -> bool:
        """고거래량 시간대 여부"""
        current_hour = self.get_current_utc_hour()
        return current_hour in self.config['high_volume_hours']
    
    def is_low_volume_time(self) -> bool:
        """저거래량 시간대 여부"""
        current_hour = self.get_current_utc_hour()
        return current_hour in self.config['low_volume_hours']
    
    def is_near_funding_time(self, tolerance_minutes=30) -> bool:
        """펀딩 시간 근처 여부"""
        now = datetime.datetime.utcnow()
        current_hour = now.hour
        current_minute = now.minute
        
        for funding_hour in self.config['funding_hours']:
            # 펀딩 시간 전후 tolerance_minutes 내인지 확인
            if abs((current_hour * 60 + current_minute) - (funding_hour * 60)) <= tolerance_minutes:
                return True
        return False
    
    def should_avoid_trading(self) -> bool:
        """거래를 피해야 하는 시간인지"""
        return self.is_near_funding_time() or self.is_low_volume_time()
    
    def get_leverage_multiplier(self) -> float:
        """현재 시간대에 맞는 레버리지 배수"""
        if self.is_high_volume_time():
            return self.config['max_leverage'] * 0.8
        elif self.is_low_volume_time():
            return self.config['min_leverage']
        else:
            return self.config['max_leverage'] * 0.5
    
    def get_optimal_position_size(self, base_amount: float) -> float:
        """최적 포지션 크기 계산"""
        multiplier = self.get_leverage_multiplier()
        
        if self.should_avoid_trading():
            return base_amount * 0.1  # 매우 작은 포지션
        elif self.is_high_volume_time():
            return base_amount * multiplier
        else:
            return base_amount * (multiplier * 0.7)
    
    def get_trading_recommendation(self) -> dict:
        """거래 추천 정보"""
        current_hour = self.get_current_utc_hour()
        
        return {
            'should_trade': not self.should_avoid_trading(),
            'current_hour_utc': current_hour,
            'is_high_volume': self.is_high_volume_time(),
            'is_low_volume': self.is_low_volume_time(),
            'near_funding': self.is_near_funding_time(),
            'leverage_multiplier': self.get_leverage_multiplier(),
            'reason': self._get_recommendation_reason()
        }
    
    def _get_recommendation_reason(self) -> str:
        """추천 이유 설명"""
        if self.is_near_funding_time():
            return "펀딩 시간 근처로 거래 회피"
        elif self.is_low_volume_time():
            return "저거래량 시간대로 거래 회피"
        elif self.is_high_volume_time():
            return "고거래량 시간대로 적극적 거래 권장"
        else:
            return "일반 거래 시간대"
