# main_aggressive.py - 수수료 극복 공격적 매매
import asyncio
from datetime import datetime
import logging
import os
from ai_trader import AggressiveAITrader
from spot.config import *


async def main():
    print("🔥 공격적 BTC AI 트레이더 v2.0")
    print("💪 수수료 극복 전용 | 24시간 무휴 | 휴식 없음")
    print("=" * 50)

    print("🎯 변경된 목표:")
    print(f"   📈 일일 수익률: 0.8% (기존 0.5%)")
    print(f"   💰 포지션 크기: ${POSITION_SIZE} (기존 $50)")
    print(f"   🔄 최대 거래: {MAX_DAILY_TRADES}회 (기존 3회)")
    print(f"   ⚡ 분석 주기: {ANALYSIS_INTERVAL//60}분 (기존 10분)")

    print("\n🔥 공격적 변경사항:")
    print("   ❌ AI 휴식 시스템 완전 제거")
    print("   📊 손절 기준 -3.5% (기존 -2%)")
    print("   💎 익절 기준 +2.8% (기존 +4%)")
    print("   ⚡ 지정가 우선 (수수료 절약)")
    print("   🎯 수수료 0.25% 미만 유지")

    print("\n💸 예상 수수료 영향:")
    daily_trades = MAX_DAILY_TRADES
    avg_fee_per_trade = POSITION_SIZE * 0.0008  # 매수+매도
    daily_fee_cost = daily_trades * avg_fee_per_trade
    target_daily_profit = POSITION_SIZE * DAILY_TARGET

    print(f"   거래당 수수료: ${avg_fee_per_trade:.2f}")
    print(f"   일일 수수료: ${daily_fee_cost:.2f}")
    print(f"   목표 수익: ${target_daily_profit:.2f}")
    print(f"   순수익: ${target_daily_profit - daily_fee_cost:.2f}")

    net_roi = ((target_daily_profit - daily_fee_cost) / POSITION_SIZE) * 100
    print(f"   실질 수익률: {net_roi:.2f}%/일")

    if net_roi < 0.3:
        print(f"   ⚠️  실질 수익률 낮음 - 더 공격적 필요")
    else:
        print(f"   ✅ 실질 수익률 양호")

    print("\n" + "=" * 50)

    choice = input("시작하시겠습니까? (yes/no): ").lower()

    if choice != 'yes':
        print("👋 안전한 투자하세요!")
        return

    # API 키 확인
    if not os.getenv('CLAUDE_API_KEY') or os.getenv(
            'CLAUDE_API_KEY') == "your_claude_api_key_here":
        print("❌ .env 파일의 CLAUDE_API_KEY 설정 필요!")
        return

    if not os.getenv('BINANCE_API_KEY') or os.getenv(
            'BINANCE_API_KEY') == "your_binance_api_key_here":
        print("❌ .env 파일의 바이낸스 API 키 설정 필요!")
        return

    print("\n🚨 경고사항:")
    print("   💰 실제 자금이 사용됩니다")
    print("   📈 목표 수익률이 높아졌습니다 (리스크 증가)")
    print("   🤖 AI는 24시간 쉬지 않고 매매합니다")
    print("   🛑 강제 중단은 Ctrl+C만 가능합니다")

    confirm = input("\n모든 위험을 이해했습니다 (I_UNDERSTAND): ")

    if confirm != "I_UNDERSTAND":
        print("❌ 확인되지 않음 - 종료")
        return

    print("\n🚀 공격적 AI 트레이더 시작...")
    print("📊 실시간 모니터링: 콘솔 로그 확인")
    print("🛑 중단: Ctrl+C")

    trader = AggressiveAITrader()

    try:
        await trader.start()

    except KeyboardInterrupt:
        print("\n⏹️  사용자 중지 요청")
        await trader.emergency_stop()

        print("\n📊 최종 세션 리포트:")
        if trader.trade_count > 0:
            success_rate = (1 - trader.consecutive_losses /
                            max(trader.trade_count, 1)) * 100
            avg_profit_per_trade = trader.daily_pnl / trader.trade_count
            fee_impact = (trader.total_fees_paid /
                          (trader.trade_count * POSITION_SIZE)) * 100

            print(f"   💰 일일 수익: {trader.daily_pnl:+.2f}%")
            print(f"   🔄 총 거래: {trader.trade_count}회")
            print(f"   📈 거래당 평균: {avg_profit_per_trade:+.2f}%")
            print(f"   🎯 성공률: {success_rate:.1f}%")
            print(f"   💸 수수료 영향: {fee_impact:.2f}%")

            if trader.daily_pnl > 0:
                print(f"   🟢 세션 성공!")

                if trader.daily_pnl >= DAILY_TARGET * 100:
                    print(
                        f"   🎉 목표 달성! ({trader.daily_pnl:.2f}% >= {DAILY_TARGET*100:.1f}%)"
                    )
                else:
                    print(
                        f"   📊 목표 미달 ({trader.daily_pnl:.2f}% < {DAILY_TARGET*100:.1f}%)"
                    )
            else:
                print(f"   🔴 세션 손실: {trader.daily_pnl:.2f}%")
                print(f"   💡 다음 세션에서 만회 기회")
        else:
            print("   📊 거래 없이 종료")

    except Exception as e:
        print(f"\n❌ 예외 발생: {e}")
        await trader.emergency_stop()

    finally:
        print("\n✅ 안전하게 종료되었습니다")

        # 중요 리마인더
        print("\n💡 다음 세션 개선사항:")
        print("   📊 오늘 결과를 분석해 AI 프롬프트 조정")
        print("   🔧 수수료 효율성 재검토")
        print("   📈 목표 수익률 현실성 점검")


if __name__ == "__main__":
    # 로깅 레벨 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  # 콘솔 출력
            logging.FileHandler('aggressive_trader.log',
                                encoding='utf-8')  # 파일 저장
        ])

    # 시작 메시지
    logging.info("=" * 60)
    logging.info("🔥 공격적 BTC AI 트레이더 시작")
    logging.info(f"📅 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"🎯 목표: 일일 {DAILY_TARGET*100:.1f}% (수수료 고려)")
    logging.info(f"💰 포지션: ${POSITION_SIZE}")
    logging.info(f"⚡ 최대거래: {MAX_DAILY_TRADES}회")
    logging.info("=" * 60)

    asyncio.run(main())
