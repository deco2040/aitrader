
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
    """메인 실행 함수"""
    print("🚀 Claude AI Trading System")
    print("=" * 50)
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 종합 테스트 실행
        print("\n📋 종합 테스트 실행 중...")
        
        # 백테스팅 시스템 테스트
        from test_comprehensive_backtesting import ComprehensiveBacktestRunner
        backtest_runner = ComprehensiveBacktestRunner()
        backtest_runner.run_all_tests()
        
        print("\n✅ 모든 시스템이 성공적으로 실행되었습니다!")
        
    except Exception as e:
        print(f"❌ 시스템 실행 중 오류 발생: {e}")
        print("🔧 문제를 수정한 후 다시 시도해주세요.")
        return False
    
    return True

if __name__ == "__main__":
    main()
