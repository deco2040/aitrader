#!/usr/bin/env python3
"""
🚀 Claude AI Trading System 종합 테스트
- 백테스팅 기능 포함
- 실제 거래 시뮬레이션
- 성능 평가 및 리포트
"""

import sys
import os
import time
import json
from datetime import datetime, timedelta

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import with error handling
try:
    from futures.futures_main import FuturesTrader
except ImportError:
    FuturesTrader = None

try:
    from futures.claude_enhanced_trader import ClaudeEnhancedTrader
except ImportError:
    ClaudeEnhancedTrader = None

try:
    from futures.futures_backtester import FuturesBacktester
except ImportError:
    FuturesBacktester = None
from futures.futures_backtester import FuturesBacktester
from futures.claude_enhanced_trader import ClaudeEnhancedTrader

class TradingSystemTester:
    """거래 시스템 종합 테스터"""

    def __init__(self):
        self.test_results = {}
        self.backtest_results = {}

    def run_comprehensive_test(self):
        """종합 테스트 실행"""
        print("🧪 Claude AI Trading System 종합 테스트 시작")
        print("=" * 60)

        # 1. 기본 모듈 테스트
        self.test_basic_modules()

        # 2. Claude Enhanced Trader 테스트
        self.test_claude_enhanced_trader()

        # 3. 백테스팅 테스트
        self.test_backtesting()

        # 4. 통합 거래 시스템 테스트
        self.test_integrated_trading_system()

        # 5. 최종 리포트 생성
        self.generate_final_report()

    def generate_final_report(self):
        """최종 테스트 리포트 생성"""
        print("\n📋 5. 최종 테스트 리포트")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)

        print(f"총 테스트: {total_tests}")
        print(f"성공: {passed_tests}")
        print(f"실패: {total_tests - passed_tests}")
        print(f"성공률: {(passed_tests/total_tests)*100:.1f}%")

        print(f"\n📊 상세 결과:")
        for test_name, result in self.test_results.items():
            status = "✅ 성공" if result else "❌ 실패"
            print(f"  {test_name}: {status}")

        if self.backtest_results:
            print(f"\n💰 백테스팅 성과:")
            print(f"  손익: ${self.backtest_results.get('profit_loss', 0):.2f}")
            print(f"  수익률: {self.backtest_results.get('roi_percent', 0):.2f}%")

        print(f"\n🎯 최종 평가:")
        if passed_tests == total_tests:
            print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
        elif passed_tests >= total_tests * 0.8:
            print("✅ 대부분의 기능이 정상 작동합니다.")
        else:
            print("⚠️ 일부 중요한 문제가 있습니다.")

    def test_basic_modules(self):
        """기본 모듈 테스트"""
        print("\n📋 1. 기본 모듈 테스트")
        print("-" * 40)

        try:
            # Dummy clients
            from futures.futures_claude_client import FuturesClaudeClient
            from futures.futures_mcp_client import FuturesMCPClient

            claude_client = FuturesClaudeClient("test_api_key")
            mcp_client = FuturesMCPClient("test_api", "test_secret")

            # 기본 기능 테스트
            signal = claude_client.generate_trading_signal("BTC/USDT", 1500)
            market_data = mcp_client.get_market_data("BTC/USDT")
            position = mcp_client.get_position("BTC/USDT")

            print(f"✅ Trading Signal: {signal}")
            print(f"✅ Market Data: {market_data['price']}")
            print(f"✅ Position: {position['size']}")

            self.test_results['basic_modules'] = True

        except Exception as e:
            print(f"❌ 기본 모듈 테스트 실패: {e}")
            self.test_results['basic_modules'] = False

    def test_claude_enhanced_trader(self):
        """Claude Enhanced Trader 테스트"""
        print("\n🧠 2. Claude Enhanced Trader 테스트")
        print("-" * 40)

        try:
            from futures.futures_mcp_client import FuturesMCPClient

            # Dummy MCP client
            mcp_client = FuturesMCPClient()

            # Claude Enhanced Trader 초기화
            trader = ClaudeEnhancedTrader("test_claude_api_key", mcp_client)

            # 지능형 분석 테스트
            signal = trader.get_intelligent_trading_signal("BTC/USDT")
            print(f"✅ 지능형 신호: {signal.get('action', 'N/A')}")
            print(f"✅ 신뢰도: {signal.get('confidence', 0)}%")

            # 시장 해석 테스트
            narrative = trader.get_market_narrative("BTC/USDT")
            print(f"✅ 시장 해석 길이: {len(narrative)} 문자")

            self.test_results['claude_enhanced'] = True

        except Exception as e:
            print(f"❌ Claude Enhanced Trader 테스트 실패: {e}")
            self.test_results['claude_enhanced'] = False

    def test_backtesting(self):
        """백테스팅 테스트"""
        print("\n📊 3. 백테스팅 시스템 테스트")
        print("-" * 40)

        try:
            # Futures Backtester 테스트
            backtester = FuturesBacktester(
                initial_capital=10000,
                commission_rate=0.001
            )

            # 테스트 거래 시뮬레이션
            print("거래 시뮬레이션 실행 중...")

            # 매수 테스트
            backtester.buy(45000, 0.1)
            backtester.buy(46000, 0.05)

            # 매도 테스트
            backtester.sell(47000, 0.08)
            backtester.sell(48000, 0.07)

            # 성능 평가
            performance = backtester.get_performance()

            print(f"✅ 최종 잔액: ${performance['final_balance']:.2f}")
            print(f"✅ 총 거래 수: {performance['total_trades']}")
            print(f"✅ 손익: ${performance['profit_loss']:.2f}")

            self.backtest_results = performance
            self.test_results['backtesting'] = True

        except Exception as e:
            print(f"❌ 백테스팅 테스트 실패: {e}")
            self.test_results['backtesting'] = False

    def test_integrated_trading_system(self):
        """통합 거래 시스템 테스트"""
        print("\n🚀 4. 통합 거래 시스템 테스트")
        print("-" * 40)

        try:
            from futures.futures_claude_client import FuturesClaudeClient
            from futures.futures_mcp_client import FuturesMCPClient

            # 클라이언트 초기화
            claude_client = FuturesClaudeClient("test_api_key")
            mcp_client = FuturesMCPClient()

            # Futures Trader 초기화
            trader = FuturesTrader(
                claude_client=claude_client,
                mcp_client=mcp_client,
                claude_api_key="test_claude_api_key"
            )

            # 기본 거래 전략 테스트
            basic_result = trader.execute_futures_trading_strategy("BTC/USDT", 1000)
            print(f"✅ 기본 거래 전략 결과: {basic_result.get('success', False)}")

            # 지능형 거래 전략 테스트
            intelligent_result = trader.execute_intelligent_trading_strategy("BTC/USDT")
            print(f"✅ 지능형 거래 전략 결과: {intelligent_result['success']}")

            if intelligent_result['success']:
                analysis = intelligent_result['analysis']
                print(f"   - 추천 행동: {analysis.get('action', 'N/A')}")
                print(f"   - 신뢰도: {analysis.get('confidence', 0)}%")

            # 시장 인텔리전스 보고서 테스트
            report = trader.get_market_intelligence_report("BTC/USDT")
            print(f"✅ 인텔리전스 보고서 생성됨 (길이: {len(report)} 문자)")

            # Spot 시스템도 테스트
            try:
                from spot.spot_claude_client import SpotClaudeClient
                spot_claude = SpotClaudeClient()
                print("✅ Spot Claude Client 초기화 성공")

                # Spot Backtester 테스트
                from spot.spot_backtester import SpotBacktester
                spot_backtester = SpotBacktester(initial_capital=5000)
                spot_backtester.buy("BTC", 50000, 0.1)
                spot_backtester.sell("BTC", 52000, 0.05)
                spot_performance = spot_backtester.get_performance()
                print(f"✅ Spot 백테스터 손익: ${spot_performance['profit_loss']:.2f}")

            except Exception as spot_e:
                print(f"⚠️ Spot 시스템 테스트 부분 실패: {spot_e}")

        except Exception as e:
            print(f"❌ 통합 거래 시스템 테스트 실패: {e}")
            self.test_results['integrated_system'] = False

    def generate_final_report(self):
        """최종 테스트 리포트 생성"""
        print("\n📋 5. 최종 테스트 리포트")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)

        print(f"총 테스트: {total_tests}")
        print(f"성공: {passed_tests}")
        print(f"실패: {total_tests - passed_tests}")
        print(f"성공률: {(passed_tests/total_tests)*100:.1f}%")

        print(f"\n📊 상세 결과:")
        for test_name, result in self.test_results.items():
            status = "✅ 성공" if result else "❌ 실패"
            print(f"  {test_name}: {status}")

        if self.backtest_results:
            print(f"\n💰 백테스팅 성과:")
            print(f"  손익: ${self.backtest_results.get('profit_loss', 0):.2f}")
            print(f"  수익률: {self.backtest_results.get('roi_percent', 0):.2f}%")

        print(f"\n🎯 최종 평가:")
        if passed_tests == total_tests:
            print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
        elif passed_tests >= total_tests * 0.8:
            print("✅ 대부분의 기능이 정상 작동합니다.")
        else:
            print("⚠️ 일부 중요한 문제가 있습니다.")

def main():
    """메인 테스트 실행"""
    tester = TradingSystemTester()
    tester.run_comprehensive_test()

    print(f"\n🕒 테스트 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()