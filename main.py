#!/usr/bin/env python3
"""
🚀 Claude AI Trading System 메인 실행 파일
- Futures와 Spot 거래 통합 시스템
- Claude AI 기반 지능형 분석
- 백테스팅 및 실시간 거래
"""

import sys
import os
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from futures.futures_main import FuturesTrader
from futures.futures_claude_client import FuturesClaudeClient
from futures.futures_mcp_client import FuturesMCPClient
from futures.claude_enhanced_trader import ClaudeEnhancedTrader
from spot.spot_main import SpotTrader
from spot.spot_claude_client import SpotClaudeClient

def main():
    """메인 거래 시스템 실행"""
    print("🚀 Claude AI Trading System 시작")
    print("=" * 60)

    symbol = "BTC/USDT"

    try:
        # 1. Futures 거래 시스템 테스트
        print("\n📊 1. Futures 거래 시스템")
        print("-" * 40)

        # Futures 클라이언트 초기화
        futures_claude = FuturesClaudeClient("demo_api_key")
        futures_mcp = FuturesMCPClient()
        trader = FuturesTrader(futures_claude, futures_mcp, "demo_claude_key")

        # 기본 거래 전략 실행
        basic_result = trader.execute_futures_trading_strategy(symbol, 1000)
        print(f"✅ 기본 전략 결과: {basic_result['success']}")
        print(f"   신호: {basic_result.get('signal', 'N/A')}")

        # 지능형 거래 전략 실행
        intelligent_result = trader.execute_intelligent_trading_strategy(symbol)
        if intelligent_result['success']:
            analysis = intelligent_result['analysis']
            print(f"✅ 지능형 전략 결과: {intelligent_result['success']}")
            print(f"   추천 행동: {analysis.get('action', 'N/A')}")
            print(f"   신뢰도: {analysis.get('confidence', 0)}%")
            print(f"   추론: {analysis.get('reasoning', 'N/A')}")
        else:
            print(f"❌ Claude 분석 실패: {intelligent_result['error']}")

        # 시장 인텔리전스 보고서 생성
        print("\n📋 Claude 시장 인텔리전스 보고서:")
        print("=" * 50)
        intelligence_report = trader.get_market_intelligence_report(symbol)
        print(intelligence_report)

        # 2. Spot 거래 시스템 테스트
        print("\n📈 2. Spot 거래 시스템")
        print("-" * 40)

        spot_claude = SpotClaudeClient("demo_api_key")
        spot_trader = SpotTrader(spot_claude)

        spot_result = spot_trader.execute_spot_trading_strategy("BTC-USD", 1000)
        print(f"✅ Spot 거래 결과: {spot_result['success']}")

        # 3. 차별화 포인트 요약
        print("\n🚀 우리 시스템의 차별화 포인트:")
        print("=" * 50)
        print("1. 📰 실시간 뉴스 분석 기반 거래 신호")
        print("2. 🧠 Claude AI 지능형 시장 해석")
        print("3. ⚖️ Futures와 Spot 통합 거래")
        print("4. 📊 포괄적인 백테스팅 시스템")
        print("5. 🕒 시간대 기반 최적화")
        print("6. 📋 실시간 리스크 관리")

        # 4. 시스템 상태 요약
        print(f"\n📊 시스템 상태 요약:")
        print(f"   Futures 시스템: {'✅ 정상' if basic_result['success'] else '❌ 오류'}")
        print(f"   Claude AI 분석: {'✅ 정상' if intelligent_result['success'] else '❌ 오류'}")
        print(f"   Spot 시스템: {'✅ 정상' if spot_result['success'] else '❌ 오류'}")

        print(f"\n🎯 전체 시스템이 성공적으로 실행되었습니다!")

    except Exception as e:
        print(f"❌ 시스템 실행 오류: {e}")
        import traceback
        traceback.print_exc()

    print(f"\n🕒 실행 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()