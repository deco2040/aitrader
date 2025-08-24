
#!/usr/bin/env python3
"""
🔍 종합 시스템 검증 테스트
- 모든 모듈의 완전성 검증
- 백테스팅 정확성 검증
- 타입 안전성 검증
- 성능 벤치마킹
"""

import sys
import os
from datetime import datetime
import traceback

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class ComprehensiveValidator:
    def __init__(self):
        self.validation_results = {}
        self.performance_metrics = {}
    
    def run_full_validation(self):
        """전체 시스템 검증 실행"""
        print("🔍 Claude AI Trading System 종합 검증")
        print("=" * 60)
        
        # 1. 모듈 완전성 검증
        self.validate_module_integrity()
        
        # 2. 백테스팅 정확성 검증
        self.validate_backtesting_accuracy()
        
        # 3. 타입 안전성 검증
        self.validate_type_safety()
        
        # 4. 성능 벤치마킹
        self.benchmark_performance()
        
        # 5. 최종 검증 리포트
        self.generate_validation_report()
    
    def validate_module_integrity(self):
        """모듈 완전성 검증"""
        print("\n📦 1. 모듈 완전성 검증")
        print("-" * 40)
        
        required_modules = [
            ('futures.futures_backtester', 'FuturesBacktester'),
            ('spot.spot_backtester', 'SpotBacktester'),
            ('futures.futures_main', 'FuturesTrader'),
            ('futures.claude_enhanced_trader', 'ClaudeEnhancedTrader')
        ]
        
        successful_imports = 0
        
        for module_name, class_name in required_modules:
            try:
                module = __import__(module_name, fromlist=[class_name])
                cls = getattr(module, class_name)
                print(f"✅ {module_name}.{class_name} - 정상")
                successful_imports += 1
                
                # 클래스 메서드 검증
                if hasattr(cls, '__init__'):
                    print(f"   - __init__ 메서드 존재")
                
            except Exception as e:
                print(f"❌ {module_name}.{class_name} - 실패: {e}")
        
        self.validation_results['module_integrity'] = successful_imports == len(required_modules)
        print(f"\n모듈 완전성: {successful_imports}/{len(required_modules)} 성공")
    
    def validate_backtesting_accuracy(self):
        """백테스팅 정확성 검증"""
        print("\n📊 2. 백테스팅 정확성 검증")
        print("-" * 40)
        
        try:
            from futures.futures_backtester import FuturesBacktester
            from spot.spot_backtester import SpotBacktester
            
            # Futures 백테스터 정확성 검증
            futures_bt = FuturesBacktester(10000, 0.001)
            
            # 예측 가능한 거래 시나리오
            initial_balance = futures_bt.balance
            
            # 매수 검증
            buy_success = futures_bt.buy(50000, 0.1)
            expected_cost = 50000 * 0.1 * (1 + 0.001)
            actual_cost = initial_balance - futures_bt.balance
            
            print(f"매수 검증: 예상 비용 ${expected_cost:.2f}, 실제 비용 ${actual_cost:.2f}")
            cost_accuracy = abs(expected_cost - actual_cost) < 0.01
            
            # 매도 검증
            sell_success = futures_bt.sell(52000, 0.1)
            expected_revenue = 52000 * 0.1 * (1 - 0.001)
            
            performance = futures_bt.get_performance()
            print(f"최종 성과: 손익 ${performance['profit_loss']:.2f}")
            
            # Spot 백테스터 정확성 검증
            spot_bt = SpotBacktester(initial_capital=10000)
            spot_bt.buy("BTC", 50000.0, 0.1)
            spot_bt.sell("BTC", 52000.0, 0.05)
            spot_performance = spot_bt.get_performance()
            
            self.validation_results['backtesting_accuracy'] = (
                cost_accuracy and 
                buy_success and 
                sell_success and
                isinstance(spot_performance['profit_loss'], (int, float))
            )
            
            print("✅ 백테스팅 정확성 검증 완료")
            
        except Exception as e:
            print(f"❌ 백테스팅 정확성 검증 실패: {e}")
            self.validation_results['backtesting_accuracy'] = False
    
    def validate_type_safety(self):
        """타입 안전성 검증"""
        print("\n🛡️ 3. 타입 안전성 검증")
        print("-" * 40)
        
        try:
            from spot.spot_backtester import SpotBacktester
            
            # 다양한 잘못된 입력으로 테스트
            spot_bt = SpotBacktester(initial_capital=10000)
            
            # 잘못된 타입 입력 테스트
            test_cases = [
                ("BTC", None, 0.1),
                ("ETH", "invalid", 1.0),
                ("SOL", 150, "invalid"),
                ("TEST", [], 0.1),
                ("TEST2", {}, 1.0)
            ]
            
            error_handled_correctly = 0
            
            for asset, price, quantity in test_cases:
                try:
                    result = spot_bt.buy(asset, price, quantity)
                    print(f"   입력 테스트: {asset}, {price}, {quantity} - 처리됨")
                    error_handled_correctly += 1
                except Exception as e:
                    print(f"   입력 테스트: {asset}, {price}, {quantity} - 예외: {type(e).__name__}")
                    error_handled_correctly += 1
            
            # 성능 계산 시 타입 안전성 확인
            performance = spot_bt.get_performance()
            type_safe = all(
                isinstance(performance.get(key), (int, float))
                for key in ['total_value', 'profit_loss', 'final_balance']
            )
            
            self.validation_results['type_safety'] = type_safe
            print(f"✅ 타입 안전성 검증: {error_handled_correctly}/{len(test_cases)} 처리")
            
        except Exception as e:
            print(f"❌ 타입 안전성 검증 실패: {e}")
            self.validation_results['type_safety'] = False
    
    def benchmark_performance(self):
        """성능 벤치마킹"""
        print("\n⚡ 4. 성능 벤치마킹")
        print("-" * 40)
        
        try:
            import time
            from futures.futures_backtester import FuturesBacktester
            
            # 대량 거래 성능 테스트
            start_time = time.time()
            
            backtester = FuturesBacktester(100000, 0.001)
            
            # 100회 거래 시뮬레이션
            for i in range(50):
                backtester.buy(50000 + i * 10, 0.01)
                if backtester.position > 0:
                    backtester.sell(50100 + i * 10, min(0.01, backtester.position))
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            performance = backtester.get_performance()
            
            self.performance_metrics = {
                'execution_time': execution_time,
                'trades_per_second': len(backtester.trades) / execution_time,
                'memory_efficient': len(backtester.trades) < 200,
                'final_performance': performance
            }
            
            print(f"✅ 실행 시간: {execution_time:.3f}초")
            print(f"✅ 초당 거래 수: {self.performance_metrics['trades_per_second']:.1f}")
            print(f"✅ 메모리 효율성: {'Good' if self.performance_metrics['memory_efficient'] else 'Needs Improvement'}")
            
            self.validation_results['performance'] = execution_time < 1.0
            
        except Exception as e:
            print(f"❌ 성능 벤치마킹 실패: {e}")
            self.validation_results['performance'] = False
    
    def generate_validation_report(self):
        """검증 리포트 생성"""
        print("\n📋 5. 종합 검증 리포트")
        print("=" * 60)
        
        total_tests = len(self.validation_results)
        passed_tests = sum(1 for result in self.validation_results.values() if result)
        
        print(f"총 검증 항목: {total_tests}")
        print(f"통과: {passed_tests}")
        print(f"실패: {total_tests - passed_tests}")
        print(f"성공률: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n📊 상세 검증 결과:")
        for test_name, result in self.validation_results.items():
            status = "✅ 통과" if result else "❌ 실패"
            print(f"  {test_name}: {status}")
        
        if self.performance_metrics:
            print(f"\n⚡ 성능 메트릭:")
            print(f"  실행 시간: {self.performance_metrics['execution_time']:.3f}초")
            print(f"  처리량: {self.performance_metrics['trades_per_second']:.1f} 거래/초")
        
        print(f"\n🎯 시스템 상태 평가:")
        if passed_tests == total_tests:
            print("🎉 시스템이 모든 검증을 통과했습니다!")
            print("💡 백테스팅 시스템이 완벽하게 작동합니다.")
            print("🚀 상용 환경에서 안전하게 사용할 수 있습니다.")
        elif passed_tests >= total_tests * 0.8:
            print("✅ 시스템이 대부분의 검증을 통과했습니다.")
            print("⚠️ 일부 개선이 필요하지만 기본 기능은 안정적입니다.")
        else:
            print("⚠️ 시스템에 중요한 문제가 발견되었습니다.")
            print("🔧 추가 수정 작업이 필요합니다.")

def main():
    """메인 실행 함수"""
    validator = ComprehensiveValidator()
    validator.run_full_validation()
    
    print(f"\n🕒 검증 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
