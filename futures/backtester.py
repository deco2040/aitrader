
# backtester.py - 선물 마진 거래 백테스트
import asyncio
import json
import logging
import random
from datetime import datetime, timedelta
from claude_client import FuturesClaudeClient
from config import *


class FuturesBacktester:

    def __init__(self):
        self.claude = FuturesClaudeClient()
        self.initial_balance = 1000
        self.balance = 1000
        self.position_size = 0.0  # BTC 포지션 (+ 롱, - 숏)
        self.entry_price = 0.0
        self.current_leverage = 0
        self.trades = []
        self.total_fees_paid = 0.0
        self.liquidation_count = 0
        self.funding_fees_paid = 0.0

        # 선물 수수료
        self.maker_fee = FEES['maker']
        self.taker_fee = FEES['taker']
        self.funding_rate_base = FEES['funding_rate']

    async def run_futures_backtest(self, price_data, days=5):
        """선물 거래 백테스트"""
        print(f"🚀 선물 마진거래 백테스팅 - {days}일간")
        print(f"💰 초기 자본: ${self.initial_balance}")
        print(f"⚡ 레버리지: {LEVERAGE}배")
        print(f"🎯 목표: 일 {DAILY_TARGET*100:.1f}%")
        print(f"🔥 최대 거래: {MAX_DAILY_TRADES}회/일")
        print(f"⚠️ 최대 손실: {MAX_DAILY_LOSS*100:.1f}%")

        daily_pnl = 0.0
        trade_count = 0
        daily_trade_count = 0
        current_day = 0

        total_samples = len(price_data)
        samples_per_day = max(24, total_samples // days)

        print(f"📊 시뮬레이션: 총 {total_samples}개 샘플, 일당 {samples_per_day}개")
        print("=" * 60)

        for i in range(0, total_samples, max(1, total_samples // (days * samples_per_day))):
            data = price_data[i]

            # 일자 변경 체크
            if i > 0 and i % samples_per_day == 0:
                current_day += 1
                print(f"\n📅 Day {current_day} 시작 - 일일거래: {daily_trade_count}회")
                daily_trade_count = 0

                # 펀딩 수수료 계산 (8시간마다, 하루 3회)
                await self._apply_funding_fees(data['price'])

            # 일일 거래 한도 체크
            if daily_trade_count >= MAX_DAILY_TRADES:
                continue

            current_time = datetime.now() - timedelta(days=days - current_day, hours=i % 24)
            
            # 현재 포트폴리오 가치 계산
            unrealized_pnl, liquidation_price, margin_ratio = self._calculate_position_metrics(data['price'])
            
            # 청산 체크
            if self._check_liquidation(data['price'], liquidation_price):
                await self._liquidate_position(data['price'])
                self.liquidation_count += 1
                print(f"💀 청산 발생! 청산가: ${liquidation_price:,.0f}")
                continue

            current_portfolio_value = self.balance + (self.position_size * data['price'] * (1 - self.taker_fee))
            current_return = ((current_portfolio_value - self.initial_balance) / self.initial_balance) * 100

            # 선물 거래 데이터
            market_data = {
                "price": data['price'],
                "change_24h": data.get('change_24h', random.uniform(-8, 8)),
                "position_size": self.position_size,
                "unrealized_pnl": unrealized_pnl,
                "margin_ratio": margin_ratio,
                "liquidation_price": liquidation_price,
                "current_leverage": self.current_leverage,
                "funding_rate": random.uniform(-0.001, 0.001),  # 랜덤 펀딩
                "daily_pnl": daily_pnl,
                "trade_count": trade_count
            }

            # 6시간마다 로깅
            if i % (samples_per_day // 4) == 0:
                pos_info = f"{'L' if self.position_size > 0 else 'S' if self.position_size < 0 else 'N'}"
                print(f"📊 {current_time.strftime('%m/%d %H:%M')} | ${data['price']:,.0f} | "
                      f"{pos_info}:{abs(self.position_size):.4f} | PnL:{unrealized_pnl:+.1f}% | "
                      f"마진:{margin_ratio:.2f} | 포트폴리오:{current_return:+.1f}%")

            try:
                # AI 결정
                decision = await self.claude.futures_analyze(market_data)

                if decision['action'] == 'buy' and self.position_size <= 0:
                    success = await self._execute_long_entry(data['price'], decision)
                    if success:
                        trade_count += 1
                        daily_trade_count += 1

                elif decision['action'] == 'sell' and self.position_size >= 0:
                    success = await self._execute_short_entry(data['price'], decision)
                    if success:
                        trade_count += 1
                        daily_trade_count += 1

                elif decision['action'] == 'close' and self.position_size != 0:
                    profit_pct = await self._execute_position_close(data['price'], decision)
                    daily_pnl += profit_pct
                    trade_count += 1
                    daily_trade_count += 1

            except KeyboardInterrupt:
                print("\n⏹️ 백테스트 중단")
                break
            except Exception as e:
                print(f"❌ 백테스트 오류: {e}")
                continue

        final_price = price_data[-1]['price'] if price_data else 50000
        await self._final_futures_results(days, trade_count, final_price)

    async def _execute_long_entry(self, price, decision):
        """롱 포지션 진입"""
        leverage = decision.get('leverage', LEVERAGE)
        position_value = POSITION_SIZE * leverage
        
        if self.balance < POSITION_SIZE:  # 마진 부족
            return False

        # 기존 숏 포지션 청산
        if self.position_size < 0:
            await self._close_existing_position(price)

        # 수수료 계산
        trading_fee = position_value * self.taker_fee
        btc_amount = position_value / price

        self.position_size = btc_amount
        self.entry_price = price
        self.current_leverage = leverage
        self.balance -= trading_fee  # 마진에서 수수료 차감
        self.total_fees_paid += trading_fee

        self.trades.append({
            'type': 'long_entry',
            'price': price,
            'amount': btc_amount,
            'leverage': leverage,
            'fee': trading_fee,
            'margin_used': POSITION_SIZE,
            'time': datetime.now()
        })

        print(f"🟢 롱 진입: ${price:,.0f} | {btc_amount:.4f} BTC | {leverage}배 | 수수료: ${trading_fee:.2f}")
        return True

    async def _execute_short_entry(self, price, decision):
        """숏 포지션 진입"""
        leverage = decision.get('leverage', LEVERAGE)
        position_value = POSITION_SIZE * leverage
        
        if self.balance < POSITION_SIZE:
            return False

        # 기존 롱 포지션 청산
        if self.position_size > 0:
            await self._close_existing_position(price)

        trading_fee = position_value * self.taker_fee
        btc_amount = position_value / price

        self.position_size = -btc_amount  # 음수로 표시
        self.entry_price = price
        self.current_leverage = leverage
        self.balance -= trading_fee
        self.total_fees_paid += trading_fee

        self.trades.append({
            'type': 'short_entry',
            'price': price,
            'amount': btc_amount,
            'leverage': leverage,
            'fee': trading_fee,
            'margin_used': POSITION_SIZE,
            'time': datetime.now()
        })

        print(f"🔴 숏 진입: ${price:,.0f} | {btc_amount:.4f} BTC | {leverage}배 | 수수료: ${trading_fee:.2f}")
        return True

    async def _execute_position_close(self, price, decision):
        """포지션 청산"""
        if self.position_size == 0:
            return 0

        close_ratio = decision.get('close_ratio', 1.0)
        close_amount = abs(self.position_size) * close_ratio
        
        # 수익/손실 계산
        if self.position_size > 0:  # 롱 포지션
            pnl_per_btc = price - self.entry_price
            profit_usd = pnl_per_btc * close_amount
        else:  # 숏 포지션
            pnl_per_btc = self.entry_price - price
            profit_usd = pnl_per_btc * close_amount

        # 레버리지 적용된 수익률
        margin_used = POSITION_SIZE * close_ratio
        profit_pct = (profit_usd / margin_used) * 100

        # 수수료
        close_value = close_amount * price
        trading_fee = close_value * self.taker_fee
        net_profit = profit_usd - trading_fee

        # 잔고 업데이트
        self.balance += margin_used + net_profit  # 마진 반환 + 순수익
        self.total_fees_paid += trading_fee

        # 부분 청산인 경우 포지션 조정
        if close_ratio < 1.0:
            self.position_size *= (1 - close_ratio)
        else:
            self.position_size = 0.0
            self.entry_price = 0.0
            self.current_leverage = 0

        self.trades.append({
            'type': 'close',
            'price': price,
            'amount': close_amount,
            'close_ratio': close_ratio,
            'profit_usd': net_profit,
            'profit_pct': profit_pct,
            'fee': trading_fee,
            'time': datetime.now()
        })

        emoji = "🟢" if profit_pct > 0 else "🔴"
        print(f"{emoji} 청산({close_ratio*100:.0f}%): ${price:,.0f} | 수익: {profit_pct:+.2f}% | 수수료: ${trading_fee:.2f}")
        
        return profit_pct

    async def _close_existing_position(self, price):
        """기존 포지션 강제 청산"""
        if self.position_size == 0:
            return

        decision = {'close_ratio': 1.0}
        await self._execute_position_close(price, decision)

    def _calculate_position_metrics(self, current_price):
        """포지션 메트릭 계산"""
        if self.position_size == 0:
            return 0, 0, 1.0

        # 미실현 손익 계산
        if self.position_size > 0:  # 롱
            unrealized_pnl_usd = (current_price - self.entry_price) * self.position_size
        else:  # 숏
            unrealized_pnl_usd = (self.entry_price - current_price) * abs(self.position_size)

        margin_used = POSITION_SIZE
        unrealized_pnl_pct = (unrealized_pnl_usd / margin_used) * 100

        # 청산가 계산 (단순화)
        if self.position_size > 0:  # 롱
            liquidation_price = self.entry_price * (1 - 0.9 / self.current_leverage)
        else:  # 숏
            liquidation_price = self.entry_price * (1 + 0.9 / self.current_leverage)

        # 마진 비율 계산
        account_value = self.balance + unrealized_pnl_usd
        margin_ratio = account_value / margin_used if margin_used > 0 else 1.0

        return unrealized_pnl_pct, liquidation_price, margin_ratio

    def _check_liquidation(self, current_price, liquidation_price):
        """청산 여부 체크"""
        if self.position_size == 0 or liquidation_price == 0:
            return False

        if self.position_size > 0:  # 롱
            return current_price <= liquidation_price
        else:  # 숏
            return current_price >= liquidation_price

    async def _liquidate_position(self, price):
        """강제 청산"""
        if self.position_size == 0:
            return

        # 청산시 마진 전액 손실
        margin_lost = POSITION_SIZE
        self.balance -= margin_lost

        self.trades.append({
            'type': 'liquidation',
            'price': price,
            'amount': abs(self.position_size),
            'loss': margin_lost,
            'time': datetime.now()
        })

        print(f"💀 청산: ${price:,.0f} | 손실: ${margin_lost:.2f}")
        
        self.position_size = 0.0
        self.entry_price = 0.0
        self.current_leverage = 0

    async def _apply_funding_fees(self, price):
        """펀딩 수수료 적용"""
        if self.position_size == 0:
            return

        # 펀딩 비율 (랜덤, 실제로는 거래소에서 조회)
        funding_rate = random.uniform(-0.001, 0.001)
        position_value = abs(self.position_size) * price
        funding_fee = position_value * funding_rate

        # 롱 포지션이면 펀딩 지급, 숏이면 수취 (단순화)
        if self.position_size > 0:
            self.balance -= funding_fee
            self.funding_fees_paid += funding_fee
        else:
            self.balance += funding_fee
            self.funding_fees_paid -= funding_fee

        if abs(funding_fee) > 0.01:
            direction = "지급" if funding_fee > 0 else "수취"
            print(f"💰 펀딩 {direction}: ${abs(funding_fee):.2f} (비율: {funding_rate*10000:+.1f}bps)")

    async def _final_futures_results(self, days, trade_count, final_price):
        """최종 결과"""
        print("\n" + "=" * 70)
        print("🚀 선물 마진거래 백테스팅 최종 결과")
        print("=" * 70)

        # 현재 포지션 평가
        current_position_value = 0
        if self.position_size != 0:
            unrealized_pnl, liquidation_price, margin_ratio = self._calculate_position_metrics(final_price)
            current_position_value = POSITION_SIZE + (POSITION_SIZE * unrealized_pnl / 100)

        total_portfolio_value = self.balance + current_position_value
        total_return = ((total_portfolio_value - self.initial_balance) / self.initial_balance) * 100
        daily_avg_return = total_return / days

        print(f"💰 자본 현황:")
        print(f"   초기 자본: ${self.initial_balance:,.0f}")
        print(f"   현재 잔고: ${self.balance:,.0f}")
        if self.position_size != 0:
            pos_type = "롱" if self.position_size > 0 else "숏"
            print(f"   현재 포지션: {pos_type} {abs(self.position_size):.4f} BTC")
            print(f"   미실현손익: {unrealized_pnl:+.2f}%")
            print(f"   청산가: ${liquidation_price:,.0f}")
        print(f"   총 포트폴리오: ${total_portfolio_value:,.0f}")

        print(f"\n📊 수익률 분석:")
        print(f"   총 수익률: {total_return:+.2f}%")
        print(f"   일일 평균: {daily_avg_return:+.2f}%")
        print(f"   목표 달성: {'✅' if daily_avg_return >= DAILY_TARGET*100 else '❌'}")

        print(f"\n💸 비용 분석:")
        print(f"   거래 수수료: ${self.total_fees_paid:.2f}")
        print(f"   펀딩 수수료: ${self.funding_fees_paid:+.2f}")
        total_costs = self.total_fees_paid + abs(self.funding_fees_paid)
        print(f"   총 비용: ${total_costs:.2f}")

        # 거래 통계
        close_trades = [t for t in self.trades if t['type'] == 'close']
        if close_trades:
            profits = [t['profit_pct'] for t in close_trades]
            win_trades = [p for p in profits if p > 0]
            win_rate = (len(win_trades) / len(profits) * 100) if profits else 0

            print(f"\n🎯 거래 성과:")
            print(f"   총 거래: {len(close_trades)}회")
            print(f"   승률: {win_rate:.1f}%")
            print(f"   평균 수익: {sum(profits)/len(profits):+.2f}%")
            print(f"   최고 수익: {max(profits):+.2f}%")
            print(f"   최대 손실: {min(profits):+.2f}%")

        print(f"\n⚠️ 리스크 분석:")
        print(f"   청산 횟수: {self.liquidation_count}회")
        if self.liquidation_count > 0:
            print(f"   청산율: {(self.liquidation_count/trade_count)*100:.1f}%")
        print(f"   최대 레버리지: {LEVERAGE}배")
        print(f"   마진 효율성: {(total_return/LEVERAGE):+.2f}%")

        # 레버리지 효과 분석
        spot_equivalent = total_return / LEVERAGE
        leverage_benefit = total_return - spot_equivalent
        print(f"\n🔥 레버리지 효과:")
        print(f"   현물 대비 수익: {total_return:+.2f}% vs {spot_equivalent:+.2f}%")
        print(f"   레버리지 이득: {leverage_benefit:+.2f}%p")

        if leverage_benefit > 0:
            print(f"   ✅ 레버리지 효과 긍정적")
        else:
            print(f"   ❌ 레버리지 효과 부정적")


def generate_futures_data(days=5):
    """선물 거래용 데이터 생성"""
    import random

    base_price = 50000
    data = []

    samples_per_day = 48
    total_samples = days * samples_per_day

    for i in range(total_samples):
        # 더 높은 변동성
        change = random.uniform(-0.04, 0.04)  # ±4%
        base_price *= (1 + change)
        base_price = max(25000, min(100000, base_price))

        # 24시간 변동률
        change_24h = random.uniform(-15, 15)

        data.append({
            'price': base_price,
            'change_24h': change_24h
        })

    return data


async def main():
    print("🚀 선물 마진거래 백테스터")
    print("⚡ 레버리지 거래 | 청산 위험 | 펀딩 수수료")
    print(f"🎯 목표: {DAILY_TARGET*100:.1f}%/일 | 레버리지: {LEVERAGE}배")

    days = int(input("\n백테스팅 기간 (일, 기본 3): ") or "3")

    print(f"\n📊 {days}일간 선물 데이터 생성...")
    price_data = generate_futures_data(days)

    print(f"🚀 선물 백테스팅 시작...")

    backtester = FuturesBacktester()

    try:
        await backtester.run_futures_backtest(price_data, days)
    except KeyboardInterrupt:
        print("\n⏹️ 백테스트 중단")


if __name__ == "__main__":
    asyncio.run(main())
