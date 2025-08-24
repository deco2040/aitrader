
#!/usr/bin/env python3
"""
🧪 백테스터 간단 테스트
"""

from backtester import UnifiedBacktester

def test_basic_trading():
    """기본 거래 테스트"""
    bt = UnifiedBacktester(10000)
    
    # 매수/매도 테스트
    assert bt.buy('BTC', 45000, 0.1) == True
    assert bt.sell('BTC', 47000, 0.1) == True
    
    perf = bt.get_performance()
    print(f"손익: ${perf['profit_loss']:.2f}")
    print("✅ 기본 거래 테스트 통과")

def test_multiple_assets():
    """다중 자산 테스트"""
    bt = UnifiedBacktester(10000)
    
    bt.buy('BTC', 45000, 0.1)
    bt.buy('ETH', 3000, 1.0)
    bt.sell('BTC', 47000, 0.05)
    
    perf = bt.get_performance()
    print(f"다중 자산 총 가치: ${perf['total_value']:.2f}")
    print("✅ 다중 자산 테스트 통과")

def main():
    print("🧪 백테스터 테스트 시작")
    print("=" * 30)
    
    test_basic_trading()
    test_multiple_assets()
    
    print("\n✅ 모든 테스트 완료")

if __name__ == "__main__":
    main()
