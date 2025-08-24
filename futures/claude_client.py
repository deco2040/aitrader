# claude_client.py - 수수료 극복 공격적 AI
import aiohttp
import json
import os
import logging
import asyncio
from datetime import datetime, timedelta
from config import *


class AggressiveClaudeClient:

    def __init__(self):
        self.api_key = os.getenv('CLAUDE_API_KEY')
        self.base_url = "https://api.anthropic.com/v1/messages"

        # 성능 추적
        self.call_count = 0
        self.decisions = []
        self.win_count = 0
        self.total_profit = 0.0

        # 🔥 공격적 최적화 (더 빈번한 AI 호출)
        self.decision_cache = {}
        self.last_ai_call = None
        self.emergency_mode = False

        # 안정성
        self.timeout = aiohttp.ClientTimeout(total=15, connect=5)

    async def aggressive_analyze(self, market_data):
        """공격적 분석 - 더 민감하고 빠른 반응"""

        # API 키 검증
        if not self.api_key or self.api_key == "your_claude_api_key_here":
            return {"action": "hold", "reason": "API키없음"}

        # 1단계: 즉시 공격적 신호
        instant_decision = self._instant_aggressive_signals(market_data)
        if instant_decision:
            logging.info(
                f"⚡ 즉시결정: {instant_decision['action']} - {instant_decision['reason']}"
            )
            self._record_decision(instant_decision)
            return instant_decision

        # 2단계: 공격적 캐시 (짧은 유효시간)
        cached = self._get_aggressive_cache(market_data)
        if cached:
            logging.info(f"💾 캐시결정: {cached['action']}")
            return cached

        # 3단계: 공격적 AI 호출 (더 자주)
        if self._needs_aggressive_ai(market_data):
            result = await self._aggressive_ai_call(market_data)
            self._update_aggressive_learning(market_data, result)
            return result

        # 4단계: 기본값
        return {"action": "hold", "reason": "대기", "confidence": 0.5}

    def _instant_aggressive_signals(self, data):
        """즉시 공격적 신호 - 더 민감한 기준"""
        price = data['price']
        change = data['change_24h']
        has_btc = data['current_position'] > 0
        pnl = data['daily_pnl']
        consecutive_losses = data.get('consecutive_losses', 0)
        aggressiveness = data.get('aggressiveness', 1.2)

        # 🔥 공격적 손절 - 더 빠르게
        if has_btc and (change < -5 or pnl < -4):
            return {
                "action": "sell",
                "reason": f"공격적손절_변동{change:.1f}%_PnL{pnl:.1f}%",
                "confidence": 0.95,
                "aggressive": True
            }

        # 🔥 기회주의적 매수 - 더 적극적
        buy_threshold = -3.0 / aggressiveness  # 공격성에 따라 조정
        if not has_btc and change < buy_threshold:
            return {
                "action": "buy",
                "reason": f"기회매수_{change:.1f}%_공격성{aggressiveness:.1f}",
                "confidence": 0.85 + (aggressiveness - 1) * 0.1,
                "aggressive": True
            }

        # 🔥 빠른 익절 - 수수료 고려한 최소 수익
        min_profit = 2.0 if consecutive_losses < 3 else 2.5  # 연속손실시 더 신중
        if has_btc and change > min_profit:
            return {
                "action": "sell",
                "reason": f"빠른익절_{change:.1f}%_최소{min_profit:.1f}%",
                "confidence": 0.80,
                "aggressive": True
            }

        # 🔥 추격매수 - 상승 추세시
        if not has_btc and 3 < change < 6 and pnl > -1:
            return {
                "action": "buy",
                "reason": f"추격매수_{change:.1f}%",
                "confidence": 0.7,
                "aggressive": True
            }

        return None

    def _get_aggressive_cache(self, data):
        """공격적 캐싱 - 더 세분화된 키"""
        # 더 정밀한 캐싱 (1K 단위, 1% 단위)
        price_zone = int(data['price'] / 1000) * 1000
        change_zone = int(data['change_24h'])  # 1% 단위
        pnl_zone = int(data['daily_pnl'])
        position_key = "long" if data['current_position'] > 0 else "cash"
        loss_key = min(data.get('consecutive_losses', 0), 5)  # 최대 5까지

        cache_key = f"{price_zone}_{change_zone}_{pnl_zone}_{position_key}_{loss_key}"

        cached = self.decision_cache.get(cache_key)
        if cached and self._is_aggressive_cache_fresh(cached):
            return {
                "action": cached['action'],
                "reason": f"{cached['reason']}_캐시",
                "confidence":
                cached.get('confidence', 0.6) * 0.9  # 캐시는 약간 낮은 신뢰도
            }

        return None

    def _needs_aggressive_ai(self, data):
        """공격적 AI 호출 필요성 - 더 자주 호출"""
        urgent_cases = [
            # 🔥 더 민감한 변동 감지
            abs(data['change_24h']) > 2,  # 3% → 2%

            # 🔥 손익 민감도 증가
            abs(data['daily_pnl']) > 1,  # 2% → 1%

            # 🔥 연속 손실 더 빨리 개입
            data.get('consecutive_losses', 0) >= 2,  # 3 → 2

            # 🔥 정기 점검 더 자주
            not self.last_ai_call or (datetime.now() - self.last_ai_call
                                      > timedelta(minutes=30)),  # 1시간 → 30분

            # 첫 분석
            self.call_count == 0,

            # 🔥 공격성 레벨 고려
            data.get('aggressiveness', 1.0) > 1.5
        ]

        return any(urgent_cases)

    async def _aggressive_ai_call(self, data):
        """공격적 AI 호출 - 더 구체적인 프롬프트"""

        # 🔥 공격적 특화 프롬프트
        aggressiveness = data.get('aggressiveness', 1.2)
        consecutive_losses = data.get('consecutive_losses', 0)

        prompt = f"""🔥 BTC 공격적 매매분석 (수수료 극복 모드):

현재상황:
- 가격: ${data['price']:,.0f} ({data['change_24h']:+.1f}%)
- 포지션: {'BTC보유 중' if data['current_position'] > 0 else 'USDT 대기 중'}
- 일일PnL: {data['daily_pnl']:+.1f}%
- 연속손실: {consecutive_losses}회
- 공격성지수: {aggressiveness:.1f}/2.0

🎯 공격적 전략 목표:
- 수수료 0.08% 극복 (매수+매도)
- 최소 0.3% 이상 수익 추구
- 빠른 회전으로 승률 확보
- 연속손실시에도 기회 포착

💪 공격적 기준:
- 진입: -{3.0/aggressiveness:.1f}% 이상 하락
- 익절: +{2.5 if consecutive_losses < 3 else 3.0:.1f}% 이상 상승
- 손절: -{3.5 + consecutive_losses * 0.5:.1f}% 이하 하락

🤖 AI 판단 요청:
{{"action": "buy/sell/hold", "reason": "구체적근거_공격성반영", "confidence": 0.7}}

즉시 JSON만 응답:"""

        # 3회 재시도로 안정성 확보
        for attempt in range(3):
            try:
                result = await self._call_anthropic_api(prompt)
                if result:
                    self.call_count += 1
                    self.last_ai_call = datetime.now()

                    # 🔥 공격적 결정에 추가 정보
                    result['ai_call'] = True
                    result['aggressiveness_used'] = aggressiveness
                    result['attempt'] = attempt + 1

                    logging.info(
                        f"🤖 공격적 AI 분석 완료 (호출#{self.call_count}, 시도{attempt+1})"
                    )
                    return result

            except Exception as e:
                logging.warning(f"AI호출 실패 {attempt+1}/3: {e}")
                if attempt < 2:
                    await asyncio.sleep(1)  # 더 짧은 재시도 간격

        # 모든 시도 실패시 공격적 긴급 모드
        self.emergency_mode = True
        emergency_action = self._emergency_aggressive_decision(data)
        logging.error(f"🚨 AI 실패 - 긴급 공격적 모드: {emergency_action['action']}")
        return emergency_action

    def _emergency_aggressive_decision(self, data):
        """AI 실패시 긴급 공격적 결정"""
        change = data['change_24h']
        has_btc = data['current_position'] > 0
        pnl = data['daily_pnl']

        # 🔥 긴급 상황에서도 공격적 판단
        if has_btc and (change < -4 or pnl < -3):
            return {"action": "sell", "reason": "긴급손절_AI실패", "confidence": 0.9}
        elif not has_btc and change < -4:
            return {"action": "buy", "reason": "긴급매수_AI실패", "confidence": 0.8}
        else:
            return {"action": "hold", "reason": "긴급대기_AI실패", "confidence": 0.3}

    async def _call_anthropic_api(self, prompt):
        """Anthropic API 호출 (기존과 동일하지만 더 빠른 타임아웃)"""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }

        payload = {
            "model": CLAUDE_MODEL,
            "max_tokens": 150,  # 공격적 모드에서 더 상세한 응답
            "temperature": 0.2,  # 약간 더 창의적
            "messages": [{
                "role": "user",
                "content": prompt
            }]
        }

        connector = aiohttp.TCPConnector(
            limit=10,  # 더 많은 연결 허용
            keepalive_timeout=15,
            enable_cleanup_closed=True)

        async with aiohttp.ClientSession(connector=connector,
                                         timeout=self.timeout) as session:

            async with session.post(self.base_url,
                                    headers=headers,
                                    json=payload) as response:

                if response.status == 200:
                    result = await response.json()
                    content = result['content'][0]['text'].strip()
                    return self._parse_aggressive_response(content)
                else:
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")

    def _parse_aggressive_response(self, content):
        """공격적 응답 파싱"""
        try:
            # JSON 추출
            if '{' in content:
                start = content.find('{')
                end = content.rfind('}') + 1
                json_data = json.loads(content[start:end])

                action = json_data.get('action', 'hold').lower()
                if action in ['buy', 'sell', 'hold']:
                    return {
                        "action":
                        action,
                        "reason":
                        json_data.get('reason', 'ai_분석')[:50],  # 더 긴 사유
                        "confidence":
                        min(json_data.get('confidence', 0.7) * 1.1,
                            0.95)  # 공격적 신뢰도 증가
                    }

        except json.JSONDecodeError:
            pass

        # 텍스트 폴백 (공격적 키워드 감지)
        content_lower = content.lower()
        if any(word in content_lower for word in ['급락', '매수', 'buy', '기회']):
            return {"action": "buy", "reason": "공격적텍스트분석", "confidence": 0.7}
        elif any(word in content_lower
                 for word in ['급등', '매도', 'sell', '익절', '손절']):
            return {"action": "sell", "reason": "공격적텍스트분석", "confidence": 0.7}
        else:
            return {"action": "hold", "reason": "파싱실패", "confidence": 0.4}

    def _update_aggressive_learning(self, market_data, decision):
        """공격적 학습 업데이트"""
        # 결정 기록
        self._record_decision(decision)

        # 🔥 더 세밀한 캐싱
        price_zone = int(market_data['price'] / 1000) * 1000
        change_zone = int(market_data['change_24h'])
        pnl_zone = int(market_data['daily_pnl'])
        position_key = "long" if market_data['current_position'] > 0 else "cash"
        loss_key = min(market_data.get('consecutive_losses', 0), 5)

        cache_key = f"{price_zone}_{change_zone}_{pnl_zone}_{position_key}_{loss_key}"

        self.decision_cache[cache_key] = {
            **decision, 'cached_at': datetime.now(),
            'market_data': market_data.copy()
        }

        # 🔥 공격적 메모리 관리 (더 많이 저장)
        if len(self.decision_cache) > 200:  # 100 → 200
            cutoff = datetime.now() - timedelta(minutes=10)  # 더 짧은 유효시간
            self.decision_cache = {
                k: v
                for k, v in self.decision_cache.items()
                if v.get('cached_at', cutoff) > cutoff
            }

    def _record_decision(self, decision):
        """결정 기록"""
        decision_record = {
            **decision, 'timestamp': datetime.now(),
            'call_number': self.call_count
        }

        self.decisions.append(decision_record)

        # 메모리 관리
        if len(self.decisions) > 500:  # 더 많은 기록 보존
            self.decisions = self.decisions[-250:]

    def _is_aggressive_cache_fresh(self, cached_item, max_age_minutes=10):
        """공격적 캐시 신선도 (더 짧은 유효시간)"""
        if 'cached_at' not in cached_item:
            return False

        age = datetime.now() - cached_item['cached_at']
        return age < timedelta(minutes=max_age_minutes)

    def record_trade_result(self, action, profit_pct):
        """거래 결과 기록 (성능 추적)"""
        if action == 'sell':
            if profit_pct > 0:
                self.win_count += 1
            self.total_profit += profit_pct

    def get_performance_stats(self):
        """성능 통계"""
        if not self.decisions:
            return {'win_rate': 0, 'avg_profit': 0, 'total_calls': 0}

        # 매도 결정만 추출
        sell_decisions = [
            d for d in self.decisions if d.get('action') == 'sell'
        ]
        total_decisions = len(self.decisions)

        # 승률 계산 (매우 단순화)
        win_rate = (self.win_count / max(len(sell_decisions), 1)) * 100
        avg_profit = self.total_profit / max(len(sell_decisions), 1)

        return {
            'win_rate': min(win_rate, 100),
            'avg_profit': avg_profit,
            'total_calls': self.call_count,
            'total_decisions': total_decisions,
            'emergency_mode': self.emergency_mode,
            'cache_size': len(self.decision_cache)
        }

    def get_optimization_stats(self):
        """최적화 통계 (기존 호환성)"""
        stats = self.get_performance_stats()

        decisions_without_ai = len(self.decisions) - self.call_count
        savings_rate = (decisions_without_ai /
                        max(len(self.decisions), 1)) * 100

        return {
            'ai_calls': self.call_count,
            'total_decisions': len(self.decisions),
            'savings_rate': f"{savings_rate:.1f}%",
            'cache_size': len(self.decision_cache),
            'emergency_mode': self.emergency_mode,
            'estimated_daily_cost':
            f"${self.call_count * 0.003:.3f}"  # 공격적 모드는 비용 약간 상승
        }
