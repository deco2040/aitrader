#!/usr/bin/env python3
"""
⏰ 시간 기반 거래 로직 테스트
- 거래량 시간대 분석
- 펀딩 시간 회피 로직
- 레버리지 최적화
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from futures_time_based_trader import TimeBasedTradingManager
import datetime

def test_time_based_trading():
    """시간대 기반 거래 로직 테스트"""
    try:
        time_manager = TimeBasedTradingManager()
        
        print("=== 시간대 기반 거래 시스템 테스트 ===")
        print(f"현재 UTC 시간: {datetime.datetime.utcnow()}")
        print(f"현재 시간(UTC): {time_manager.get_current_utc_hour()}시")
        
        # 거래량 시간대 테스트
        print(f"\n거래량이 많은 시간대 여부: {time_manager.is_high_volume_time()}")
        print(f"거래량이 적은 시간대 여부: {time_manager.is_low_volume_time()}")
        print(f"레버리지 배수: {time_manager.get_leverage_multiplier()}")
        
        # 펀딩 시간 테스트
        print(f"\n펀딩 시간 근처 여부: {time_manager.is_near_funding_time()}")
        print(f"거래 회피 시간 여부: {time_manager.should_avoid_trading()}")
        
        # 포지션 크기 테스트
        base_size = 1000
        optimized_size = time_manager.get_optimal_position_size(base_size)
        print(f"\n기본 포지션 크기: ${base_size}")
        print(f"최적화된 포지션 크기: ${optimized_size:.2f}")
        
        # 거래 추천
        recommendation = time_manager.get_trading_recommendation()
        print(f"\n=== 거래 추천 ===")
        for key, value in recommendation.items():
            print(f"{key}: {value}")
        
        print("\n✅ 시간대 기반 거래 테스트 완료")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")

if __name__ == "__main__":
    test_time_based_trading() key, value in recommendation.items():
            print(f"{key}: {value}")
        
        # 24시간 시뮬레이션
        print(f"\n=== 24시간 거래 시뮬레이션 ===")
        for hour in range(24):
            is_high_volume = hour in [8, 9, 10, 14, 15, 16, 20, 21, 22]
            is_funding_time = hour in [0, 8, 16]
            print(f"시간 {hour:02d}:00 - 고거래량: {is_high_volume}, 펀딩시간: {is_funding_time}")
            
        print("✅ 시간대 기반 거래 테스트 완료")
        return True
        
    except Exception as e:
        print(f"❌ 시간대 기반 거래 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    test_time_based_trading()