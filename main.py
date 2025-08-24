#!/usr/bin/env python3
"""
🚀 Claude AI Trading System - Main Entry Point
- Futures와 Spot 거래 시스템 통합
- 백테스팅 기능 포함
- 종합 테스트 실행
"""

import sys
import os
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """메인 엔트리 포인트"""
    print("🚀 Claude AI Trading System")
    print("=" * 50)
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # 종합 검증 테스트 실행
        print("\n📋 종합 검증 테스트 실행 중...")

        from test_comprehensive_validation import ComprehensiveValidator
        validator = ComprehensiveValidator()
        validator.run_full_validation()

        print("\n✅ 시스템이 성공적으로 실행되었습니다!")

    except Exception as e:
        print(f"❌ 시스템 실행 중 오류 발생: {e}")
        print("🔧 문제를 수정한 후 다시 시도해주세요.")
        
        # 기본 모듈 테스트 시도
        try:
            print("\n🔧 기본 백테스팅 테스트 시도 중...")
            from futures.futures_backtester import FuturesBacktester
            bt = FuturesBacktester(10000, 0.001)
            bt.buy(45000, 0.1)
            bt.sell(47000, 0.1)
            performance = bt.get_performance()
            print(f"✅ 기본 백테스팅 성공: 손익 ${performance['profit_loss']:.2f}")
        except Exception as basic_e:
            print(f"❌ 기본 테스트도 실패: {basic_e}")

if __name__ == "__main__":
    main()