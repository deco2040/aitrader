# split_order.py - 수수료 극복용 최적화
import asyncio
import logging
from datetime import datetime
from spot.config import *

class OptimizedSplitOrder:
    def __init__(self, mcp_client):
        self.mcp = mcp_client
        self.active_splits = {}
        self.emergency_stop = False

        # 수수료 (현실)
        self.maker_fee = 0.0002  # 0.02%
        self.taker_fee = 0.0004  # 0.04%

    async def optimized_split_buy(self, symbol, total_usdt, current_price, aggressiveness=1.0):
        """수수료 최적화 분할매수"""

        # 🔥 공격성에 따른 동적 분할 수 조정
        if aggressiveness > 1.5:
            # 매우 공격적: 큰 덩어리로 빠르게
            splits = min(3, MAX_SPLITS)
            interval_base = 180  # 3분
        elif aggressiveness > 1.2:
            # 공격적: 보통 분할
            splits = min(4, MAX_SPLITS) 
            interval_base = 300  # 5분
        else:
            # 일반적: 기존 방식
            splits = MAX_SPLITS
            interval_base = 600  # 10분

        # 수수료 효율성 체크
        split_amount = total_usdt / splits
        fee_per_split = split_amount * self.taker_fee
        fee_ratio = fee_per_split / split_amount

        # 수수료 비중이 너무 크면 분할 수 줄임
        if fee_ratio > 0.001:  # 0.1% 이상
            splits = max(2, int(splits * 0.7))
            split_amount = total_usdt / splits
            logging.info(f"💸 수수료 최적화: {splits}분할로 조정")

        logging.info(f"⚡ 최적화 분할매수: {splits}분할 | 공격성 {aggressiveness:.1f}")

        # 첫 분할 즉시 실행
        first_result = await self._execute_optimized_split(
            symbol, split_amount, current_price, 1, splits
        )

        if first_result['success']:
            self.active_splits[symbol] = {
                'splits': splits,
                'completed': 1,
                'split_amount': split_amount,
                'start_price': current_price,
                'total_btc': first_result['btc_amount'],
                'total_cost': first_result['total_cost'],
                'total_fees': first_result['fee'],
                'interval': interval_base,
                'aggressiveness': aggressiveness
            }

            # 나머지 분할 진행
            asyncio.create_task(self._continue_optimized_splits(symbol))
            return True, first_result['total_cost'], first_result['btc_amount']

        return False, 0, 0

    async def _execute_optimized_split(self, symbol, usdt_amount, current_price, split_num, total_splits):
        """최적화된 단일 분할 실행"""
        try:
            # 🔥 지정가 우선 시도 (수수료 절약)
            maker_price = current_price * 0.999  # 0.1% 아래 지정가

            # 지정가 주문 시도
            maker_order = await self.mcp.create_order(
                symbol, 'limit', 'buy', usdt_amount / maker_price, maker_price
            )

            if maker_order:
                # 10초 대기
                await asyncio.sleep(10)

                # 체결 확인
                if maker_order.get('status') == 'closed':
                    # 지정가 체결 성공 (수수료 절약)
                    fee = usdt_amount * self.maker_fee
                    btc_amount = (usdt_amount - fee) / maker_price

                    logging.info(f"✅ 지정가 체결 {split_num}/{total_splits}: 수수료 절약 ${(self.taker_fee - self.maker_fee) * usdt_amount:.2f}")

                    return {
                        'success': True,
                        'btc_amount': btc_amount,
                        'total_cost': usdt_amount,
                        'fee': fee,
                        'order_type': 'maker'
                    }

            # 🔥 지정가 실패시 시장가로 즉시 체결
            logging.info(f"⚡ 시장가 전환 {split_num}/{total_splits}")

            fee = usdt_amount * self.taker_fee
            btc_amount = (usdt_amount - fee) / current_price

            market_order = await self.mcp.create_order(
                symbol, 'market', 'buy', btc_amount
            )

            if market_order and market_order.get('status') == 'closed':
                actual_cost = market_order.get('cost', usdt_amount)
                actual_fee = market_order.get('fee', {}).get('cost', fee)

                return {
                    'success': True,
                    'btc_amount': btc_amount,
                    'total_cost': actual_cost,
                    'fee': actual_fee,
                    'order_type': 'taker'
                }

        except Exception as e:
            logging.error(f"❌ 분할 {split_num} 실행 오류: {e}")

        return {'success': False}

    async def _continue_optimized_splits(self, symbol):
        """최적화된 분할 진행"""
        split_info = self.active_splits[symbol]
        consecutive_maker_fails = 0

        while (split_info['completed'] < split_info['splits'] and not self.emergency_stop):

            # 🔥 동적 간격 조정
            base_interval = split_info['interval']
            aggressiveness = split_info['aggressiveness']

            # 공격적일수록 짧은 간격
            actual_interval = int(base_interval / aggressiveness)

            # 지정가 연속 실패시 간격 단축
            if consecutive_maker_fails >= 2:
                actual_interval = int(actual_interval * 0.5)
                logging.info("⚡ 간격 단축 - 빠른 매수 모드")

            await asyncio.sleep(actual_interval)

            # 시장 상황 체크
            ticker = await self.mcp.fetch_ticker(symbol)
            if not ticker:
                break

            current_price = ticker['last']
            start_price = split_info['start_price']
            price_change = (current_price - start_price) / start_price

            # 🔥 공격성에 따른 중단 기준 조정
            stop_threshold = 0.12 / aggressiveness  # 공격적일수록 더 참음

            if abs(price_change) > stop_threshold:
                direction = "상승" if price_change > 0 else "하락"
                logging.warning(f"⚠️ {direction} {abs(price_change)*100:.1f}% - 분할 중단")
                break

            # 다음 분할 실행
            next_split = split_info['completed'] + 1
            split_result = await self._execute_optimized_split(
                symbol, split_info['split_amount'], current_price, next_split, split_info['splits']
            )

            if split_result['success']:
                # 통계 업데이트
                split_info['completed'] += 1
                split_info['total_btc'] += split_result['btc_amount']
                split_info['total_cost'] += split_result['total_cost']
                split_info['total_fees'] += split_result['fee']

                # 지정가/시장가 성공률 추적
                if split_result['order_type'] == 'maker':
                    consecutive_maker_fails = 0
                    logging.info("💰 지정가 성공 - 수수료 절약")
                else:
                    consecutive_maker_fails += 1

                # 진행 상황 로깅
                avg_price = split_info['total_cost'] / split_info['total_btc']
                fee_impact = (split_info['total_fees'] / split_info['total_cost']) * 100

                logging.info(f"📊 분할 진행: {split_info['completed']}/{split_info['splits']} | 평균가: ${avg_price:.0f} | 수수료: {fee_impact:.2f}%")

                # 🔥 수수료 효율성 실시간 모니터링
                if fee_impact > 0.25:  # 0.25% 초과시
                    logging.warning(f"💸 고수수료 경고: {fee_impact:.2f}% - 남은 분할 검토")

                    # 나머지 분할을 한번에 처리할지 결정
                    remaining_splits = split_info['splits'] - split_info['completed']
                    if remaining_splits <= 2:
                        logging.info("⚡ 나머지 분할 통합 실행")

                        # 남은 금액 한번에 처리
                        remaining_amount = split_info['split_amount'] * remaining_splits
                        final_result = await self._execute_optimized_split(
                            symbol, remaining_amount, current_price, 
                            split_info['completed'] + 1, split_info['splits']
                        )

                        if final_result['success']:
                            split_info['completed'] = split_info['splits']
                            split_info['total_btc'] += final_result['btc_amount']
                            split_info['total_cost'] += final_result['total_cost']
                            split_info['total_fees'] += final_result['fee']

                        break
            else:
                logging.error("❌ 분할 실행 실패 - 중단")
                break

        # 완료 리포트
        if symbol in self.active_splits:
            final_info = self.active_splits[symbol]
            self._generate_completion_report(symbol, final_info)
            del self.active_splits[symbol]

    def _generate_completion_report(self, symbol, final_info):
        """완료 리포트 생성"""
        avg_price = final_info['total_cost'] / final_info['total_btc']
        total_fee_impact = (final_info['total_fees'] / final_info['total_cost']) * 100
        completion_rate = (final_info['completed'] / final_info['splits']) * 100

        # 수수료 절약 효과 계산
        max_possible_fee = final_info['total_cost'] * self.taker_fee
        actual_savings = max_possible_fee - final_info['total_fees']
        savings_pct = (actual_savings / max_possible_fee) * 100 if max_possible_fee > 0 else 0

        logging.info(f"🎉 분할매수 완료 리포트:")
        logging.info(f"   ₿  총 BTC: {final_info['total_btc']:.6f}")
        logging.info(f"   💰 총 비용: ${final_info['total_cost']:.2f}")
        logging.info(f"   📊 평균가: ${avg_price:.0f}")
        logging.info(f"   💸 수수료: ${final_info['total_fees']:.2f} ({total_fee_impact:.2f}%)")
        logging.info(f"   📈 완료율: {completion_rate:.0f}%")
        logging.info(f"   💎 수수료 절약: ${actual_savings:.2f} ({savings_pct:.1f}%)")

        # 성과 평가
        if total_fee_impact < 0.15:
            logging.info("   🟢 수수료 효율: 우수")
        elif total_fee_impact < 0.25:
            logging.info("   🟡 수수료 효율: 양호") 
        else:
            logging.info("   🔴 수수료 효율: 개선 필요")

    def get_split_status(self, symbol):
        """분할 상태 조회"""
        if symbol in self.active_splits:
            info = self.active_splits[symbol]
            fee_efficiency = (info['total_fees'] / info['total_cost']) * 100

            return {
                'active': True,
                'progress': f"{info['completed']}/{info['splits']}",
                'completion_rate': (info['completed'] / info['splits']) * 100,
                'total_cost': info['total_cost'],
                'total_fees': info['total_fees'],
                'fee_efficiency': fee_efficiency,
                'avg_price': info['total_cost'] / info['total_btc'] if info['total_btc'] > 0 else 0,
                'aggressiveness': info['aggressiveness']
            }
        return {'active': False}

    async def emergency_stop_all(self):
        """긴급 중단"""
        self.emergency_stop = True

        if self.active_splits:
            logging.warning("🚨 분할매수 긴급 중단:")

            for symbol, info in self.active_splits.items():
                completion_rate = (info['completed'] / info['splits']) * 100
                fee_so_far = info['total_fees']
                potential_savings = info['split_amount'] * (info['splits'] - info['completed']) * (self.taker_fee - self.maker_fee)

                logging.warning(f"   📊 {symbol}: {completion_rate:.0f}% 완료")
                logging.warning(f"   💸 지불 수수료: ${fee_so_far:.2f}")
                logging.warning(f"   💎 예상 절약: ${potential_savings:.2f} (중단으로 손실)")

        self.active_splits.clear()
        logging.critical("🚨 모든 분할매수 중단 완료")