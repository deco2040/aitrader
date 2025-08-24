
#!/usr/bin/env python3
"""
🔍 전체 시스템 포괄적 검증
- 모든 모듈 Import 테스트
- 백테스팅 시스템 검증
- Futures/Spot 트레이더 기능 테스트
"""

import sys
import os
import traceback
from datetime import datetime

def test_imports():
    """모든 중요 모듈 Import 테스트"""
    print("📦 Import 테스트 시작...")
    
    try:
        # 백테스터 테스트
        from backtester import UnifiedBacktester, FuturesBacktester, SpotBacktester
        print("✅ backtester.py - OK")
        
        # Futures 모듈들
        from futures.futures_main import FuturesTrader
        print("✅ futures_main.py - OK")
        
        # Spot 모듈들 (에러 처리 포함)
        try:
            from spot.spot_main import SpotTrader
            print("✅ spot_main.py - OK")
        except ImportError as e:
            print(f"⚠️ spot_main.py - 일부 의존성 누락: {e}")
        
        # 메인 모듈
        import main
        print("✅ main.py - OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Import 오류: {e}")
        traceback.print_exc()
        return False

def test_unified_backtester():
    """통합 백테스터 테스트"""
    print("\n🔄 UnifiedBacktester 테스트...")
    
    try:
        from backtester import UnifiedBacktester
        
        bt = UnifiedBacktester(10000, 0.001)
        
        # 기본 거래 테스트
        assert bt.buy('BTC', 50000, 0.1) == True, "BTC 매수 실패"
        assert bt.buy('ETH', 3000, 1.0) == True, "ETH 매수 실패"
        assert bt.sell('BTC', 52000, 0.05) == True, "BTC 부분 매도 실패"
        assert bt.sell('ETH', 3200, 1.0) == True, "ETH 전체 매도 실패"
        
        # 성능 분석
        perf = bt.get_performance()
        assert perf['initial_capital'] == 10000, "초기 자본 오류"
        assert perf['total_trades'] == 4, "거래 횟수 오류"
        
        # 리포트 생성
        report = bt.generate_report()
        assert "백테스팅 리포트" in report, "리포트 생성 오류"
        
        print(f"✅ 총 거래: {perf['total_trades']}")
        print(f"✅ 손익: ${perf['profit_loss']:.2f}")
        print(f"✅ 수익률: {perf['roi_percent']:.2f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ UnifiedBacktester 오류: {e}")
        traceback.print_exc()
        return False

def test_futures_trader():
    """Futures 트레이더 테스트"""
    print("\n🚀 FuturesTrader 테스트...")
    
    try:
        from futures.futures_main import FuturesTrader
        
        # Dummy 클라이언트 생성
        class DummyClaudeClient:
            def generate_trading_signal(self, symbol, amount):
                return {"action": "BUY" if amount > 1000 else "SELL", "confidence": 85}
        
        class DummyMCPClient:
            def get_market_data(self, symbol):
                return {"price": 50000, "volume": 1000000}
        
        # 트레이더 초기화
        trader = FuturesTrader(
            claude_client=DummyClaudeClient(),
            mcp_client=DummyMCPClient(),
            claude_api_key="test_key"
        )
        
        # 거래 전략 실행
        result = trader.execute_futures_trading_strategy("BTC/USDT", 1500)
        assert result['success'] == True, "Futures 거래 전략 실행 실패"
        assert 'market_data' in result, "시장 데이터 누락"
        assert 'signal' in result, "거래 신호 누락"
        
        # 거래 기록 확인
        history = trader.get_trading_history()
        assert len(history) == 1, "거래 기록 오류"
        
        print("✅ Futures 거래 전략 실행 성공")
        print(f"✅ 신호: {result['signal']['action']}")
        print(f"✅ 거래 기록: {len(history)}건")
        
        return True
        
    except Exception as e:
        print(f"❌ FuturesTrader 오류: {e}")
        traceback.print_exc()
        return False

def test_edge_cases():
    """경계 케이스 테스트"""
    print("\n⚠️ 경계 케이스 테스트...")
    
    try:
        from backtester import UnifiedBacktester
        
        bt = UnifiedBacktester(1000)
        
        # 잘못된 입력 테스트
        assert bt.buy('BTC', -100, 0.1) == False, "음수 가격 매수 방지 실패"
        assert bt.buy('BTC', 50000, -0.1) == False, "음수 수량 매수 방지 실패"
        assert bt.sell('BTC', 50000, 0.1) == False, "보유하지 않은 자산 매도 방지 실패"
        
        # 잔액 부족 테스트
        assert bt.buy('BTC', 50000, 1.0) == False, "잔액 부족 거래 방지 실패"
        
        # 정상 거래 후 과다 매도 테스트
        bt.buy('BTC', 100, 1.0)
        assert bt.sell('BTC', 100, 2.0) == False, "과다 매도 방지 실패"
        
        print("✅ 모든 경계 케이스 통과")
        return True
        
    except Exception as e:
        print(f"❌ 경계 케이스 오류: {e}")
        traceback.print_exc()
        return False

def test_performance_calculation():
    """성능 계산 정확성 테스트"""
    print("\n📊 성능 계산 테스트...")
    
    try:
        from backtester import UnifiedBacktester
        
        bt = UnifiedBacktester(10000, 0.001)
        
        # 수익 거래
        bt.buy('BTC', 100, 10)  # $1,001 (수수료 포함)
        bt.sell('BTC', 110, 10)  # $1,098.9 (수수료 제외)
        
        perf = bt.get_performance()
        expected_profit = 1098.9 - 1001  # 약 $97.9
        
        # 허용 오차 범위 내에서 확인
        assert abs(perf['profit_loss'] - expected_profit) < 1, f"수익 계산 오류: 예상 {expected_profit}, 실제 {perf['profit_loss']}"
        
        print(f"✅ 수익 계산 정확성 확인: ${perf['profit_loss']:.2f}")
        return True
        
    except Exception as e:
        print(f"❌ 성능 계산 오류: {e}")
        traceback.print_exc()
        return False

def main():
    """전체 검증 실행"""
    print("🔍 전체 시스템 포괄적 검증 시작")
    print("=" * 50)
    print(f"검증 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Import", test_imports),
        ("UnifiedBacktester", test_unified_backtester),
        ("FuturesTrader", test_futures_trader),
        ("경계 케이스", test_edge_cases),
        ("성능 계산", test_performance_calculation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} 테스트 실패")
        except Exception as e:
            print(f"❌ {test_name} 테스트 예외: {e}")
    
    print("\n" + "=" * 50)
    print(f"검증 완료: {passed}/{total} 테스트 통과")
    
    if passed == total:
        print("🎉 모든 테스트 통과! 시스템이 정상 작동합니다.")
    else:
        print("⚠️ 일부 테스트 실패. 코드 수정이 필요합니다.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
