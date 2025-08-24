
#!/usr/bin/env python3
"""
🔧 통합 테스트 - 모든 기능 검증
"""

import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from futures.futures_backtester import FuturesBacktester
from spot.spot_backtester import SpotBacktester
from futures.futures_main import FuturesTrader
from futures.claude_enhanced_trader import ClaudeEnhancedTrader

class IntegrationTester:
    def __init__(self):
        self.results = {}
        
    def run_all_tests(self):
        """모든 통합 테스트 실행"""
        print("🔧 통합 테스트 시작")
        print("=" * 50)
        
        # 1. 백테스팅 안정성 테스트
        self.test_backtesting_stability()
        
        # 2. 타입 안전성 테스트
        self.test_type_safety()
        
        # 3. 에러 처리 테스트
        self.test_error_handling()
        
        # 4. 결과 출력
        self.print_results()
    
    def test_backtesting_stability(self):
        """백테스팅 안정성 테스트"""
        try:
            # Futures 백테스터 테스트
            futures_bt = FuturesBacktester(10000, 0.001)
            futures_bt.buy(45000, 0.1)
            futures_bt.sell(47000, 0.05)
            futures_perf = futures_bt.get_performance()
            
            # Spot 백테스터 테스트
            spot_bt = SpotBacktester(initial_capital=10000)
            spot_bt.buy("BTC", 45000, 0.1)
            spot_bt.sell("BTC", 47000, 0.05)
            spot_perf = spot_bt.get_performance()
            
            self.results['backtesting_stability'] = True
            print("✅ 백테스팅 안정성 테스트 통과")
            
        except Exception as e:
            self.results['backtesting_stability'] = False
            print(f"❌ 백테스팅 안정성 테스트 실패: {e}")
    
    def test_type_safety(self):
        """타입 안전성 테스트"""
        try:
            spot_bt = SpotBacktester()
            
            # 다양한 타입으로 테스트
            test_assets = {
                'BTC': 0.1,
                'ETH': 1.0,
                'SOL': 10
            }
            
            for asset, qty in test_assets.items():
                spot_bt.holdings[asset] = qty
            
            performance = spot_bt.get_performance()
            assert 'total_value' in performance
            assert isinstance(performance['total_value'], (int, float))
            
            self.results['type_safety'] = True
            print("✅ 타입 안전성 테스트 통과")
            
        except Exception as e:
            self.results['type_safety'] = False
            print(f"❌ 타입 안전성 테스트 실패: {e}")
    
    def test_error_handling(self):
        """에러 처리 테스트"""
        try:
            futures_bt = FuturesBacktester(1000, 0.001)
            
            # 잘못된 입력값 테스트
            result1 = futures_bt.buy(-100, 0.1)  # 음수 가격
            result2 = futures_bt.buy(45000, -0.1)  # 음수 수량
            result3 = futures_bt.buy(50000, 10)  # 잔액 부족
            
            assert result1 == False
            assert result2 == False
            assert result3 == False
            
            self.results['error_handling'] = True
            print("✅ 에러 처리 테스트 통과")
            
        except Exception as e:
            self.results['error_handling'] = False
            print(f"❌ 에러 처리 테스트 실패: {e}")
    
    def print_results(self):
        """결과 출력"""
        print(f"\n📋 통합 테스트 결과")
        print("=" * 50)
        
        passed = sum(1 for v in self.results.values() if v)
        total = len(self.results)
        
        for test, result in self.results.items():
            status = "✅ 통과" if result else "❌ 실패"
            print(f"{test}: {status}")
        
        print(f"\n성공률: {passed}/{total} ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print("🎉 모든 통합 테스트 통과!")
        else:
            print("⚠️ 일부 테스트 실패")

if __name__ == "__main__":
    tester = IntegrationTester()
    tester.run_all_tests()
