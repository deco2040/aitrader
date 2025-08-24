# ai_trader.py - 수수료 극복 공격적 매매
import asyncio
import logging
from datetime import datetime, timedelta
from claude_client import AggressiveClaudeClient
from spot.mcp_client import MCPClient
from spot.split_order import OptimizedSplitOrder
from spot.config import *

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class AggressiveAITrader:
    def __init__(self):
        self.claude = AggressiveClaudeClient()
        self.mcp = MCPClient()
        self.split = OptimizedSplitOrder(self.mcp)
        self.running = False

        # 포지션 상태
        self.current_position = 0.0
        self.entry_price = 0.0
        self.total_entry_cost = 0.0

        # 수익/손실 추적
        self.daily_pnl = 0.0
        self.total_fees_paid = 0.0
        self.trade_count = 0

        # 🔥 AI 휴식 완전 제거
        self.consecutive_losses = 0  # 카운트만, 휴식 없음
        self.forced_rest_until = None  # 사용 안함

        # 🔥 실제 바이낸스 수수료
        self.maker_fee = 0.0002  # 0.02%
        self.taker_fee = 0.0004  # 0.04%
        self.daily_funding = 0.00015  # 0.015% (일일)

    async def start(self):
        self.running = True
        logging.info("🚀 공격적 AI 트레이더 시작 (휴식 없음)")
        logging.info(f"🎯 현실적 목표: 일 0.8% (수수료 0.2% 감안)")
        logging.info(f"💰 포지션 사이즈: ${POSITION_SIZE} (수수료 희석)")
        logging.info(f"🤖 24시간 무휴 AI 가동")

        try:
            await asyncio.gather(
                self.aggressive_trading_loop(),
                self.dynamic_strategy_loop(),
                self.smart_risk_loop()
            )
        except Exception as e:
            logging.error(f"❌ 시스템 오류: {e}")
            await self.emergency_stop()

    async def aggressive_trading_loop(self):
        """공격적 매매 루프 (휴식 없음)"""
        while self.running:
            try:
                # 🔥 거래 제한 대폭 완화
                if self.trade_count >= MAX_DAILY_TRADES:
                    await asyncio.sleep(ANALYSIS_INTERVAL)
                    continue

                ticker = await self.mcp.fetch_ticker(SYMBOL)
                balance = await self.mcp.fetch_balance()

                if not ticker or not balance:
                    await asyncio.sleep(30)  # 짧은 대기 후 재시도
                    continue

                current_price = ticker['last']
                change_24h = ticker.get('percentage', 0)

                # 🔥 더 민감한 시장 데이터
                market_data = {
                    "price": current_price,
                    "change_24h": change_24h,
                    "balance": balance,
                    "current_position": self.current_position,
                    "daily_pnl": self.daily_pnl,
                    "trade_count": self.trade_count,
                    "fees_paid": self.total_fees_paid,
                    "consecutive_losses": self.consecutive_losses,
                    "aggressiveness": self._calculate_aggressiveness()
                }

                # AI 분석 (휴식 없이)
                decision = await self.claude.aggressive_analyze(market_data)
                await self._execute_aggressive_trade(decision, current_price, balance)

                # 상태 로깅
                fee_impact = (self.total_fees_paid / max(self.trade_count * POSITION_SIZE, 1)) * 100
                logging.info(f"📊 ${current_price:,.0f} ({change_24h:+.1f}%) | PnL:{self.daily_pnl:+.2f}% | 수수료영향:{fee_impact:.2f}% | {decision['action']}")

            except Exception as e:
                logging.error(f"❌ 매매루프 오류: {e}")
                # 오류 발생해도 계속 진행

            await asyncio.sleep(ANALYSIS_INTERVAL)

    def _calculate_aggressiveness(self):
        """공격성 레벨 계산"""
        base_aggro = 1.0

        # 손실 상황일수록 더 공격적
        if self.daily_pnl < -2:
            base_aggro += 0.5
        elif self.daily_pnl < -5:
            base_aggro += 1.0

        # 수수료 부담 고려
        if self.trade_count > 0:
            fee_burden = self.total_fees_paid / (self.trade_count * POSITION_SIZE)
            if fee_burden > 0.003:  # 0.3% 이상
                base_aggro += 0.3

        # 연속 손실시 더 신중하게 (휴식은 없음)
        if self.consecutive_losses >= 3:
            base_aggro *= 0.8
        elif self.consecutive_losses >= 5:
            base_aggro *= 0.6

        return min(base_aggro, 2.0)

    async def _execute_aggressive_trade(self, decision, current_price, balance):
        """공격적 거래 실행"""
        if decision['action'] == 'hold':
            return

        try:
            if decision['action'] == 'buy' and self.current_position == 0:
                # 🔥 수수료 고려한 동적 포지션 크기
                dynamic_size = self._calculate_dynamic_position_size(current_price)

                success, actual_cost, actual_amount = await self.split.optimized_split_buy(
                    SYMBOL, dynamic_size, current_price, 
                    aggressiveness=self._calculate_aggressiveness()
                )

                if success:
                    self.current_position = actual_amount
                    self.entry_price = current_price
                    self.total_entry_cost = actual_cost
                    self.trade_count += 1

                    logging.info(f"🟢 공격적 매수: 실제비용 ${actual_cost:.0f} | 공격성 {self._calculate_aggressiveness():.1f}")

            elif decision['action'] == 'sell' and self.current_position > 0:
                # 분할매수 즉시 중단
                await self.split.emergency_stop_all()

                # 🔥 수수료 고려한 정확한 매도
                gross_value = self.current_position * current_price
                sell_fee = gross_value * self.taker_fee
                net_received = gross_value - sell_fee

                result = await self.mcp.create_order(SYMBOL, 'market', 'sell', self.current_position)

                if result and result.get('status') == 'closed':
                    # 정확한 수익률 계산
                    profit_usd = net_received - self.total_entry_cost
                    profit_pct = (profit_usd / self.total_entry_cost) * 100

                    self.daily_pnl += profit_pct
                    self.total_fees_paid += sell_fee
                    self.trade_count += 1

                    # 🔥 연속 손실 카운트만 (휴식은 없음)
                    if profit_pct < 0:
                        self.consecutive_losses += 1
                        logging.warning(f"⚠️ 연속 손실 {self.consecutive_losses}회 - 더 신중하게")
                    else:
                        self.consecutive_losses = 0
                        logging.info("✅ 연속 손실 해소")

                    # 포지션 클리어
                    self.current_position = 0.0
                    self.entry_price = 0.0
                    self.total_entry_cost = 0.0

                    profit_emoji = "🟢" if profit_pct >= 0 else "🔴"
                    logging.info(f"{profit_emoji} 매도완료: 실질수익 {profit_pct:+.2f}% | 수수료: ${sell_fee:.2f}")

        except Exception as e:
            logging.error(f"❌ 거래 실행 실패: {e}")

    def _calculate_dynamic_position_size(self, current_price):
        """동적 포지션 크기 계산 (수수료 최적화)"""
        base_size = POSITION_SIZE

        # 변동성이 클 때 크기 조정
        if abs(self.daily_pnl) > 3:
            base_size *= 1.2  # 20% 증가

        # 연속 손실시 크기 조정 (휴식 대신)
        if self.consecutive_losses >= 3:
            base_size *= 0.8  # 20% 감소
        elif self.consecutive_losses >= 5:
            base_size *= 0.6  # 40% 감소

        # 수수료 효율성 확보
        min_efficient_size = 80  # 최소 $80
        return max(base_size, min_efficient_size)

    async def dynamic_strategy_loop(self):
        """동적 전략 조정 (지속적)"""
        while self.running:
            await asyncio.sleep(STRATEGY_INTERVAL)

            try:
                # 수수료 효율성 분석
                if self.trade_count > 0:
                    avg_fee_per_trade = self.total_fees_paid / self.trade_count
                    fee_impact_pct = (avg_fee_per_trade * 2) / POSITION_SIZE * 100

                    logging.info(f"💸 수수료 분석: 거래당 ${avg_fee_per_trade:.2f} ({fee_impact_pct:.2f}%)")

                    # 수수료 부담이 클 경우 전략 조정
                    if fee_impact_pct > 0.3:
                        logging.warning("⚡ 고수수료 모드: 더 큰 수익 추구")
                        # 여기서 claude에게 더 공격적 매매 지시 가능

                # AI 성능 통계
                stats = self.claude.get_performance_stats()
                logging.info(f"🧠 AI 통계: 승률 {stats.get('win_rate', 0):.1f}% | 평균수익 {stats.get('avg_profit', 0):.2f}%")

            except Exception as e:
                logging.error(f"❌ 전략루프 오류: {e}")

    async def smart_risk_loop(self):
        """스마트 리스크 관리 (휴식 없음)"""
        while self.running:
            await asyncio.sleep(RISK_INTERVAL)

            try:
                # 🔥 휴식 시스템 완전 제거, 경고만
                if self.consecutive_losses >= 5:
                    logging.warning(f"⚠️ 연속 {self.consecutive_losses}회 손실 - AI가 학습중")
                    # 휴식 없이 계속 진행

                if self.consecutive_losses >= 8:
                    logging.critical(f"🚨 연속 {self.consecutive_losses}회 손실 - 포지션 크기 축소중")
                    # 포지션만 줄이고 계속 매매

                # 일일 손실 한도만 유지 (하드 스톱)
                if abs(self.daily_pnl) >= MAX_DAILY_LOSS * 100:
                    logging.critical(f"🚨 일일 손실 한도 도달: {self.daily_pnl:.2f}% - 하드 스톱")
                    await self.emergency_stop()
                    break

                # 수수료 대비 손익 분석
                if self.current_position > 0:
                    ticker = await self.mcp.fetch_ticker(SYMBOL)
                    if ticker:
                        current_price = ticker['last']
                        current_profit_pct = ((current_price - self.entry_price) / self.entry_price) * 100

                        # 수수료 고려 실질 수익
                        fee_impact = 0.08  # 매수+매도 수수료 0.08%
                        real_profit = current_profit_pct - fee_impact

                        if real_profit < -5:
                            logging.warning(f"⚠️ 실질 손실 {real_profit:.2f}% (수수료 포함)")

            except Exception as e:
                logging.error(f"❌ 리스크루프 오류: {e}")

    async def emergency_stop(self):
        """긴급 정지 (하드 스톱만)"""
        self.running = False
        logging.critical("🚨 하드 스톱 실행 - 일일 한도 도달")

        await self.split.emergency_stop_all()

        # 포지션 정리
        if self.current_position > 0:
            try:
                ticker = await self.mcp.fetch_ticker(SYMBOL)
                if ticker:
                    current_price = ticker['last']
                    gross_value = self.current_position * current_price
                    emergency_fee = gross_value * self.taker_fee

                    await self.mcp.create_order(SYMBOL, 'market', 'sell', self.current_position)
                    logging.warning(f"🚨 긴급 매도: 예상 수령액 ${gross_value - emergency_fee:.0f}")
            except:
                pass

        # 최종 통계
        if self.trade_count > 0:
            avg_profit = self.daily_pnl / self.trade_count
            total_fee_impact = (self.total_fees_paid / (self.trade_count * POSITION_SIZE)) * 100

            logging.info(f"📊 세션 결과:")
            logging.info(f"   💰 일일 수익: {self.daily_pnl:.2f}%")
            logging.info(f"   🔄 거래 횟수: {self.trade_count}회")
            logging.info(f"   💸 총 수수료: ${self.total_fees_paid:.2f}")
            logging.info(f"   📈 거래당 평균: {avg_profit:.2f}%")
            logging.info(f"   🔍 수수료 영향: {total_fee_impact:.2f}%")

# 공격적 Claude 클라이언트
class AggressiveClaudeClient:
    def __init__(self):
        self.api_key = os.getenv('CLAUDE_API_KEY')
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.call_count = 0
        self.decisions = []

    async def aggressive_analyze(self, market_data):
        """공격적 분석"""

        # 즉시 판단 (더 민감하게)
        instant = self._instant_aggressive_signals(market_data)
        if instant:
            return instant

        # AI 호출 (더 자주)
        if self._needs_aggressive_analysis(market_data):
            return await self._call_aggressive_ai(market_data)

        return {"action": "hold", "reason": "대기"}

    def _instant_aggressive_signals(self, data):
        """즉시 판단 (더 공격적)"""
        price = data['price']
        change = data['change_24h']
        has_btc = data['current_position'] > 0
        pnl = data['daily_pnl']
        aggressiveness = data.get('aggressiveness', 1.0)

        # 🔥 더 공격적인 진입 조건
        if not has_btc and change < -4 * aggressiveness:
            return {"action": "buy", "reason": f"공격적급락매수_{change:.1f}%", "confidence": 0.9}

        # 🔥 빠른 익절 (수수료 고려)
        if has_btc and change > 2.5:
            return {"action": "sell", "reason": f"빠른익절_{change:.1f}%", "confidence": 0.85}

        # 🔥 손절 기준 완화 (더 참음)
        if has_btc and (change < -4.5 or pnl < -4):
            return {"action": "sell", "reason": f"확장손절_{change:.1f}%", "confidence": 0.8}

        return None

    def _needs_aggressive_analysis(self, data):
        """AI 호출 필요성 (더 자주)"""
        return any([
            abs(data['change_24h']) > 2,  # 3%→2%
            abs(data['daily_pnl']) > 1.5,  # 2%→1.5%
            data['consecutive_losses'] >= 2,  # 더 빨리 개입
            self.call_count == 0
        ])

    async def _call_aggressive_ai(self, data):
        """공격적 AI 호출"""
        prompt = f"""BTC 공격적 매매분석 (수수료 0.08% 감안):

현재: ${data['price']:,.0f} ({data['change_24h']:+.1f}%)
포지션: {'BTC보유' if data['current_position'] > 0 else 'USDT보유'}  
일일PnL: {data['daily_pnl']:+.1f}%
연속손실: {data.get('consecutive_losses', 0)}회
공격성: {data.get('aggressiveness', 1.0):.1f}

수수료 극복 전략:
- 최소 0.3% 이상 수익 추구
- 손절은 -3.5%까지 허용
- 빠른 익절로 승률 확보

{{"action":"buy/sell/hold","reason":"근거"}}"""

        try:
            # API 호출 구현 (기존과 동일)
            self.call_count += 1
            # 실제 API 호출 코드...
            return {"action": "hold", "reason": "AI분석중", "confidence": 0.7}
        except:
            return {"action": "hold", "reason": "AI오류", "confidence": 0.3}

    def get_performance_stats(self):
        """성능 통계"""
        if not self.decisions:
            return {'win_rate': 0, 'avg_profit': 0}

        # 간단한 통계 계산
        return {
            'win_rate': 60,  # 임시값
            'avg_profit': 0.8  # 임시값
        }