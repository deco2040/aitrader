
#!/usr/bin/env python3
"""
🚀 Claude AI Trading System - 간소화된 메인
"""

from datetime import datetime
from backtester import UnifiedBacktester

def run_simple_backtest():
    """간단한 백테스팅 실행"""
    print("📊 백테스팅 시작")
    print("-" * 30)
    
    bt = UnifiedBacktester(10000)
    
    # 샘플 거래들
    bt.buy('BTC', 45000, 0.1)
    bt.buy('ETH', 3000, 1.0)
    bt.sell('BTC', 47000, 0.1)
    bt.sell('ETH', 3200, 0.8)
    
    # 결과 출력
    print(bt.generate_report())

def main():
    print("🚀 Claude AI Trading System")
    print("=" * 40)
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        run_simple_backtest()
        print("✅ 시스템이 성공적으로 실행되었습니다!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
