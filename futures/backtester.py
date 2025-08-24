# backtester.py - 공격적 설정 백테스트
import asyncio
import json
import logging
import random
from datetime import datetime, timedelta
from claude_client import AggressiveClaudeClient
from config import *


class AggressiveBacktester:

    def __init__(self):
        self.claude = AggressiveClaudeClient()
        self.initial_balance = 1000
        self.balance = 1000
        self.btc_amount = 0.0
        self.entry_price = 0.0
        self.trades = []
        self.total_fees_paid = 0.0
        self.consecutive_losses = 0

        # 🔥 공격적 수수료 (현실 반영)
        self.maker_fee = 0.0002  # 0.02%
        self.taker_fee = 0.0004  # 0.04%
        self.daily_funding = 0.00015  # 0.015%/일

    async def run_aggressive_backtest(self, price_data, days=5):
        """공격적 설정 백테스트"""
        print(f"🔥 공격적 AI 백테스팅 - {days}일간")
        print(f"💰 초기 자본: ${self.initial_balance}")
        print(
            f"🎯 목표: 일 {DAILY_TARGET*100:.1f}% (기존 0.5% 대비 {(DAILY_TARGET/0.005-1)*100:+.0f}%)"
        )
        print(f"⚡ 최대 거래: {MAX_DAILY_TRADES}회/일 (기존 3회 대비)")
        print(f"🤖 AI 휴식: 없음 (24시간 가동)")

        daily_pnl = 0.0
        trade_count = 0
        daily_trade_count = 0
        current_day = 0

        total_samples = len(price_data)
        samples_per_day = max(24, total_samples // days)  # 하루 24개 샘플

        print(f"📊 시뮬레이션: 총 {total_samples}개 샘플, 일당 {samples_per_day}개")
        print("=" * 60)

        for i in range(0, total_samples,
                       max(1, total_samples // (days * samples_per_day))):
            data = price_data[i]

            # 일자 변경 체크
            if i > 0 and i % samples_per_day == 0:
                current_day += 1
                print(f"\n📅 Day {current_day} 시작 - 일일거래: {daily_trade_count}회")
                daily_trade_count = 0

                # 펀딩 수수료 차감 (하루 한번)
                if self.btc_amount > 0:
                    funding_cost = (self.btc_amount *
                                    data['price']) * self.daily_funding
                    self.balance -= funding_cost
                    self.total_fees_paid += funding_cost
                    print(f"💸 펀딩수수료: ${funding_cost:.2f}")

            # 일일 거래 한도 체크 (공격적으로 완화)
            if daily_trade_count >= MAX_DAILY_TRADES:
                continue

            current_time = datetime.now() - timedelta(days=days - current_day,
                                                      hours=i % 24)
            current_portfolio_value = self.balance + (self.btc_amount *
                                                      data['price'] *
                                                      (1 - self.taker_fee))
            current_return = (
                (current_portfolio_value - self.initial_balance) /
                self.initial_balance) * 100

            # 🔥 공격적 시장 데이터
            market_data = {
                "price":
                data['price'],
                "change_24h":
                data.get('change_24h', random.uniform(-8, 8)),
                "current_position":
                self.btc_amount,
                "daily_pnl":
                daily_pnl,
                "trade_count":
                trade_count,
                "consecutive_losses":
                self.consecutive_losses,
                "aggressiveness":
                self._calculate_aggressiveness(daily_pnl, trade_count)
            }

            # 수익률이 하루 목표 달성시 로깅
            daily_target_usd = self.initial_balance * DAILY_TARGET
            current_daily_profit = current_portfolio_value - self.initial_balance

            if i % (samples_per_day // 4) == 0:  # 6시간마다 로깅
                print(
                    f"📊 {current_time.strftime('%m/%d %H:%M')} | ${data['price']:,.0f} | "
                    f"포트폴리오: ${current_portfolio_value:,.0f} ({current_return:+.1f}%) | "
                    f"일일목표: {(current_daily_profit/daily_target_usd)*100:.0f}%"
                )

            try:
                # 🔥 AI 결정 (휴식 없음)
                decision = await self.claude.aggressive_analyze(market_data)

                if decision['action'] == 'buy' and self.btc_amount == 0:
                    success = self._execute_aggressive_buy(
                        data['price'], market_data)
                    if success:
                        trade_count += 1
                        daily_trade_count += 1

                elif decision['action'] == 'sell' and self.btc_amount > 0:
                    profit_pct = self._execute_aggressive_sell(data['price'])
                    daily_pnl += profit_pct
                    trade_count += 1
                    daily_trade_count += 1

                    if profit_pct > 0:
                        self.consecutive_losses = 0
                        print(f"🟢 익절: {profit_pct:+.2f}% | 연속손실 초기화")
                    else:
                        self.consecutive_losses += 1
                        # 🔥 휴식 없음, 단지 카운트만
                        print(
                            f"🔴 손절: {profit_pct:+.2f}% | 연속손실 {self.consecutive_losses}회"
                        )

                        if self.consecutive_losses >= 5:
                            print(
                                f"⚠️  연속 {self.consecutive_losses}회 손실 - AI 학습중 (휴식 없음)"
                            )

            except KeyboardInterrupt:
                print("\n⏹️  백테스트 중단")
                break
            except Exception as e:
                print(f"❌ 백테스트 오류: {e}")
                continue

        final_price = price_data[-1]['price'] if price_data else 50000
        await self._final_aggressive_results(days, trade_count, final_price)

    def _calculate_aggressiveness(self, daily_pnl, trade_count):
        """공격성 계산"""
        base = 1.2  # 기본적으로 공격적

        if daily_pnl < -3:
            base += 0.5  # 손실시 더 공격적
        elif daily_pnl < -6:
            base += 1.0

        if self.consecutive_losses >= 3:
            base *= 0.9  # 연속 손실시 살짝 보수적
        elif self.consecutive_losses >= 6:
            base *= 0.8

        return min(base, 2.0)

    def _execute_aggressive_buy(self, price, market_data):
        """공격적 매수 (더 큰 포지션)"""
        # 🔥 동적 포지션 크기
        aggressiveness = market_data.get('aggressiveness', 1.2)
        position_size = POSITION_SIZE * aggressiveness

        if self.balance < position_size:
            return False

        # 🔥 지정가 우선 시도 (30% 확률로 성공)
        maker_success_rate = 0.3
        if random.random() < maker_success_rate:
            # 지정가 성공 (수수료 절약)
            avg_price = price * 0.999  # 0.1% 저렴하게
            trading_fee = position_size * self.maker_fee
            order_type = "지정가"
        else:
            # 시장가 (일반 수수료)
            avg_price = price
            trading_fee = position_size * self.taker_fee
            order_type = "시장가"

        # 실제 매수
        net_buy_amount = position_size - trading_fee
        btc_bought = net_buy_amount / avg_price

        self.btc_amount = btc_bought
        self.entry_price = avg_price
        self.balance -= position_size
        self.total_fees_paid += trading_fee

        self.trades.append({
            'type':
            'buy',
            'price':
            avg_price,
            'amount':
            btc_bought,
            'usdt_spent':
            position_size,
            'fee':
            trading_fee,
            'order_type':
            order_type,
            'aggressiveness':
            market_data.get('aggressiveness', 1.0),
            'time':
            datetime.now()
        })

        print(
            f"🟢 {order_type} 매수: ${avg_price:,.0f} | BTC: {btc_bought:.6f} | 수수료: ${trading_fee:.2f} | 공격성: {market_data.get('aggressiveness', 1.0):.1f}"
        )
        return True

    def _execute_aggressive_sell(self, price):
        """공격적 매도"""
        if self.btc_amount == 0:
            return 0

        # 🔥 지정가 시도 (20% 확률)
        maker_success_rate = 0.2  # 매도시 지정가 성공률 낮음
        if random.random() < maker_success_rate:
            sell_price = price * 1.001  # 0.1% 비싸게
            trading_fee_rate = self.maker_fee
            order_type = "지정가"
        else:
            sell_price = price
            trading_fee_rate = self.taker_fee
            order_type = "시장가"

        gross_sell_value = self.btc_amount * sell_price
        trading_fee = gross_sell_value * trading_fee_rate
        net_sell_value = gross_sell_value - trading_fee

        # 수익 계산 (매수시 지출 기준)
        last_buy_trade = next(
            (t for t in reversed(self.trades) if t['type'] == 'buy'), None)
        if last_buy_trade:
            position_cost = last_buy_trade['usdt_spent']
            profit_usd = net_sell_value - position_cost
            profit_pct = (profit_usd / position_cost) * 100
        else:
            profit_pct = 0

        # 잔고 업데이트
        self.balance += net_sell_value
        self.total_fees_paid += trading_fee

        self.trades.append({
            'type': 'sell',
            'price': sell_price,
            'amount': self.btc_amount,
            'gross_value': gross_sell_value,
            'net_value': net_sell_value,
            'fee': trading_fee,
            'order_type': order_type,
            'profit_usd': profit_usd if last_buy_trade else 0,
            'profit_pct': profit_pct,
            'time': datetime.now()
        })

        # 포지션 클리어
        self.btc_amount = 0.0
        self.entry_price = 0.0

        return profit_pct

    async def _final_aggressive_results(self, days, trade_count, final_price):
        """공격적 백테스트 최종 결과"""
        print("\n" + "=" * 70)
        print("🔥 공격적 AI 백테스팅 최종 결과")
        print("=" * 70)

        # 현재 포지션 평가
        current_btc_value = 0
        if self.btc_amount > 0:
            gross_value = self.btc_amount * final_price
            estimated_sell_fee = gross_value * self.taker_fee
            current_btc_value = gross_value - estimated_sell_fee

        total_portfolio_value = self.balance + current_btc_value
        total_return = ((total_portfolio_value - self.initial_balance) /
                        self.initial_balance) * 100
        daily_avg_return = total_return / days

        print(f"💰 자본 현황:")
        print(f"   초기 자본: ${self.initial_balance:,.0f}")
        print(f"   현재 USDT: ${self.balance:,.0f}")
        if self.btc_amount > 0:
            print(f"   현재 BTC: {self.btc_amount:.6f} BTC")
            print(f"   예상 매도가치: ${current_btc_value:,.0f} (수수료 차감)")
        print(f"   총 포트폴리오: ${total_portfolio_value:,.0f}")

        print(f"\n📊 수익률 분석:")
        print(f"   총 수익률: {total_return:+.2f}%")
        print(f"   일일 평균: {daily_avg_return:+.2f}%")
        print(
            f"   목표 대비: {(daily_avg_return/DAILY_TARGET/100-1)*100:+.1f}% ({'✅달성' if daily_avg_return >= DAILY_TARGET*100 else '❌미달'})"
        )

        # 🔥 공격적 설정 효과 분석
        conservative_target = 0.5  # 기존 목표
        aggressive_boost = (daily_avg_return - conservative_target)
        print(f"   공격적 효과: {aggressive_boost:+.2f}%p")

        print(f"\n💸 수수료 상세 분석:")
        print(f"   총 지불 수수료: ${self.total_fees_paid:.2f}")
        print(
            f"   수수료율: {(self.total_fees_paid/self.initial_balance)*100:.2f}%")
        if trade_count > 0:
            avg_fee_per_trade = self.total_fees_paid / trade_count
            print(f"   거래당 평균: ${avg_fee_per_trade:.2f}")

        # 거래 통계
        sell_trades = [t for t in self.trades if t['type'] == 'sell']
        buy_trades = [t for t in self.trades if t['type'] == 'buy']

        if sell_trades:
            profits = [t['profit_pct'] for t in sell_trades]
            win_trades = [p for p in profits if p > 0]
            win_rate = (len(win_trades) / len(profits) * 100) if profits else 0
            avg_profit = sum(profits) / len(profits)

            print(f"\n🎯 거래 성과:")
            print(
                f"   총 거래: {len(sell_trades)}회 (목표: {MAX_DAILY_TRADES * days}회)"
            )
            print(f"   승률: {win_rate:.1f}%")
            print(f"   평균 수익: {avg_profit:+.2f}%")
            print(f"   최고 수익: {max(profits):+.2f}%")
            print(f"   최대 손실: {min(profits):+.2f}%")

            # 지정가/시장가 분석
            maker_orders = [
                t for t in self.trades if t.get('order_type') == '지정가'
            ]
            if maker_orders:
                maker_ratio = len(maker_orders) / len(self.trades) * 100
                maker_fee_saved = len(maker_orders) * POSITION_SIZE * (
                    self.taker_fee - self.maker_fee)
                print(f"   지정가 비율: {maker_ratio:.1f}%")
                print(f"   수수료 절약: ${maker_fee_saved:.2f}")

        # 🔥 연속 손실 분석 (휴식 없음의 영향)
        print(f"\n🤖 AI 연속성 분석:")
        print(
            f"   최대 연속손실: {max([t.get('consecutive_losses', 0) for t in self.trades] + [0])}회"
        )
        print(f"   휴식 없이 진행: ✅")
        print(f"   24시간 가동: ✅")

        if self.consecutive_losses >= 5:
            print(f"   ⚠️  현재 연속손실: {self.consecutive_losses}회 (일반적으론 휴식)")
            print(f"   💪 하지만 AI는 계속 학습하며 매매")

        # 목표 달성도 평가
        print(f"\n🎯 목표 달성 평가:")
        target_reached = daily_avg_return >= DAILY_TARGET * 100

        if target_reached:
            print(
                f"   🎉 목표 달성! ({daily_avg_return:.2f}% >= {DAILY_TARGET*100:.1f}%)"
            )

            if daily_avg_return >= DAILY_TARGET * 100 * 1.5:
                print(
                    f"   🚀 목표 초과달성! (+{((daily_avg_return/DAILY_TARGET/100)-1)*100:.0f}%)"
                )

        else:
            shortfall = (DAILY_TARGET * 100) - daily_avg_return
            print(f"   📊 목표 미달: -{shortfall:.2f}%p")

            # 개선 방안 제시
            print(f"\n💡 개선 방안:")
            if win_rate < 60:
                print(f"   📈 승률 개선 필요 (현재 {win_rate:.1f}% < 목표 60%)")
            if avg_profit < 0.8:
                print(f"   💰 평균 수익 확대 필요 (현재 {avg_profit:.2f}% < 목표 0.8%)")
            if len(sell_trades) < MAX_DAILY_TRADES * days * 0.8:
                print(f"   ⚡ 거래 빈도 확대 필요")

        # 🔥 현실성 검토
        print(f"\n⚠️  현실적 고려사항:")
        realistic_return = daily_avg_return * 0.8  # 실제 환경에서 20% 감소 예상
        print(f"   실제 환경 예상: {realistic_return:+.2f}%/일")
        print(f"   슬리피지 영향: -0.05~0.1%")
        print(f"   네트워크 지연: 일부 기회 상실")
        print(f"   감정적 개입: AI 장점 상쇄 가능")

        if realistic_return >= 0.3:
            print(f"   🟢 현실적으로 수익 가능")
        elif realistic_return >= 0:
            print(f"   🟡 현실에선 간신히 수익")
        else:
            print(f"   🔴 현실에선 손실 위험")

        print(f"\n💎 최종 판단:")
        if daily_avg_return >= DAILY_TARGET * 100 and win_rate >= 55:
            print(f"   ✅ 공격적 설정 효과적!")
            print(f"   💪 휴식 제거로 기회 확대 성공")
            print(f"   🚀 실전 적용 권장")
        elif daily_avg_return >= DAILY_TARGET * 100 * 0.8:
            print(f"   🟡 공격적 설정 양호")
            print(f"   🔧 일부 조정으로 개선 가능")
        else:
            print(f"   🔴 공격적 설정 재검토 필요")
            print(f"   📉 목표 하향 조정 또는 전략 변경")


def generate_volatile_data(days=5):
    """변동성 높은 BTC 데이터 생성"""
    import random

    base_price = 50000
    data = []

    # 하루 48개 샘플 (30분 간격)
    samples_per_day = 48
    total_samples = days * samples_per_day

    for i in range(total_samples):
        # 🔥 더 높은 변동성 (±2% → ±3%)
        change = random.uniform(-0.03, 0.03)
        base_price *= (1 + change)

        # 가격 범위 제한
        base_price = max(30000, min(80000, base_price))

        # 24시간 변동률 (더 극단적)
        change_24h = random.uniform(-12, 12)

        data.append({'price': base_price, 'change_24h': change_24h})

    return data


async def main():
    print("🔥 공격적 설정 백테스터")
    print("💪 수수료 극복 전용 | 휴식 없음 | 24시간 가동")
    print("🎯 목표 수익률: 0.8%/일 (기존 0.5% 대비 60% 상승)")

    days = int(input("\n백테스팅 기간 (일, 기본 3): ") or "3")

    # API 키 체크
    import os
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv('CLAUDE_API_KEY')
    if not api_key or api_key == "your_claude_api_key_here":
        print("⚠️  실제 Claude API 없이 시뮬레이션 모드")
        simulate_mode = True
    else:
        simulate_mode = False
        print("✅ Claude API 연결됨")

    print(f"\n📊 {days}일간 고변동성 데이터 생성...")
    price_data = generate_volatile_data(days)

    print(f"🚀 공격적 백테스팅 시작...")
    print(f"   📈 목표: 일 {DAILY_TARGET*100:.1f}%")
    print(f"   ⚡ 최대거래: {MAX_DAILY_TRADES}회/일")
    print(f"   🤖 AI 휴식: 없음")
    print(f"   💰 포지션: ${POSITION_SIZE}")

    backtester = AggressiveBacktester()

    try:
        await backtester.run_aggressive_backtest(price_data, days)

    except KeyboardInterrupt:
        print("\n⏹️  백테스트 중단")

        # 중간 결과라도 표시
        if backtester.trades:
            print(f"\n📊 중간 결과:")
            sell_trades = [t for t in backtester.trades if t['type'] == 'sell']
            if sell_trades:
                profits = [t['profit_pct'] for t in sell_trades]
                avg_profit = sum(profits) / len(profits)
                print(f"   평균 수익: {avg_profit:+.2f}%")
                print(f"   거래 횟수: {len(sell_trades)}회")

    print(f"\n💡 다음 단계:")
    print(f"   🔧 설정이 만족스럽다면 main_aggressive.py 실행")
    print(f"   📊 불만족스럽다면 config_realistic.py 조정")
    print(f"   🎯 목표 수익률을 더 보수적으로 낮출 수도 있음")


if __name__ == "__main__":
    asyncio.run(main())
