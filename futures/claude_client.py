
# claude_client.py - 선물 마진 거래 전용 AI
import aiohttp
import json
import os
import logging
import asyncio
from datetime import datetime, timedelta
from config import *


class FuturesClaudeClient:

    def __init__(self):
        self.api_key = os.getenv('CLAUDE_API_KEY')
        self.base_url = "https://api.anthropic.com/v1/messages"

        # 선물 거래 추적
        self.call_count = 0
        self.decisions = []
        self.win_count = 0
        self.total_profit = 0.0
        self.liquidation_warnings = 0

        # 선물 특화 캐시
        self.decision_cache = {}
        self.last_ai_call = None
        self.funding_aware_cache = {}

        # 안정성
        self.timeout = aiohttp.ClientTimeout(total=15, connect=5)

    async def futures_analyze(self, market_data):
        """선물 거래 전용 분석"""

        # API 키 검증
        if not self.api_key or self.api_key == "your_claude_api_key_here":
            return {"action": "hold", "reason": "API키없음"}

        # 1단계: 긴급 선물 신호 (청산 위험 등)
        urgent_decision = self._urgent_futures_signals(market_data)
        if urgent_decision:
            logging.critical(f"🚨 긴급: {urgent_decision['action']} - {urgent_decision['reason']}")
            self._record_decision(urgent_decision)
            return urgent_decision

        # 2단계: 펀딩 시간 체크
        funding_decision = self._funding_time_check(market_data)
        if funding_decision:
            logging.info(f"💰 펀딩체크: {funding_decision['action']} - {funding_decision['reason']}")
            return funding_decision

        # 3단계: 선물 캐시 확인
        cached = self._get_futures_cache(market_data)
        if cached:
            logging.info(f"💾 캐시: {cached['action']}")
            return cached

        # 4단계: AI 호출 필요성 체크
        if self._needs_futures_ai(market_data):
            result = await self._futures_ai_call(market_data)
            self._update_futures_learning(market_data, result)
            return result

        # 5단계: 기본값
        return {"action": "hold", "reason": "대기중", "confidence": 0.5}

    def _urgent_futures_signals(self, data):
        """긴급 선물 신호 - 청산 위험 등"""
        position_size = data.get('position_size', 0)
        unrealized_pnl = data.get('unrealized_pnl', 0)
        margin_ratio = data.get('margin_ratio', 1.0)
        liquidation_price = data.get('liquidation_price', 0)
        current_price = data['price']
        change = data['change_24h']

        # 🚨 청산 위험 체크
        if liquidation_price > 0 and position_size != 0:
            if position_size > 0:  # 롱 포지션
                distance_to_liq = (current_price - liquidation_price) / current_price
            else:  # 숏 포지션
                distance_to_liq = (liquidation_price - current_price) / current_price

            if distance_to_liq < 0.15:  # 청산가 15% 이내
                self.liquidation_warnings += 1
                return {
                    "action": "close",
                    "reason": f"청산위험_{distance_to_liq*100:.1f}%접근",
                    "confidence": 0.99,
                    "urgent": True,
                    "close_ratio": 1.0  # 전량 청산
                }

        # 🚨 마진 부족 경고
        if margin_ratio < RISK_MANAGEMENT['margin_ratio_min']:
            return {
                "action": "close",
                "reason": f"마진부족_{margin_ratio:.2f}",
                "confidence": 0.95,
                "urgent": True,
                "close_ratio": 0.7  # 70% 청산
            }

        # 🚨 급격한 손실
        if unrealized_pnl < FUTURES_RULES['panic_sell']:
            return {
                "action": "close",
                "reason": f"급격손실_{unrealized_pnl:.1f}%",
                "confidence": 0.90,
                "urgent": True,
                "close_ratio": 0.8
            }

        # 🎯 빠른 익절 (레버리지 고려)
        if unrealized_pnl > FUTURES_RULES['take_profit']:
            return {
                "action": "close",
                "reason": f"목표달성_{unrealized_pnl:.1f}%",
                "confidence": 0.85,
                "close_ratio": 0.5  # 50% 부분 청산
            }

        return None

    def _funding_time_check(self, data):
        """펀딩 시간 체크"""
        if not FUTURES_RULES['funding_aware']:
            return None

        current_hour = datetime.utcnow().hour
        position_size = data.get('position_size', 0)
        funding_rate = data.get('funding_rate', 0)

        # 펀딩 시간 30분 전
        funding_soon = any(abs(current_hour - ft) < 1 for ft in FEES['funding_times'])

        if funding_soon and position_size != 0:
            # 불리한 펀딩일 경우 청산 고려
            if (position_size > 0 and funding_rate > 0.0005) or \
               (position_size < 0 and funding_rate < -0.0005):
                return {
                    "action": "close",
                    "reason": f"불리한펀딩_회피_{funding_rate*10000:.1f}bps",
                    "confidence": 0.75,
                    "close_ratio": 0.8
                }

        return None

    def _needs_futures_ai(self, data):
        """선물 AI 호출 필요성"""
        urgent_cases = [
            # 선물 특화 트리거
            abs(data['change_24h']) > 2.0,
            abs(data.get('unrealized_pnl', 0)) > 1.5,
            data.get('margin_ratio', 1.0) < 0.3,
            data.get('position_size', 0) == 0,  # 포지션 없을 때

            # 정기 점검
            not self.last_ai_call or (datetime.now() - self.last_ai_call > timedelta(minutes=30)),

            # 첫 분석
            self.call_count == 0,

            # 청산 경고 이력
            self.liquidation_warnings > 0
        ]

        return any(urgent_cases)

    async def _futures_ai_call(self, data):
        """선물 전용 AI 호출"""
        
        position_size = data.get('position_size', 0)
        unrealized_pnl = data.get('unrealized_pnl', 0)
        margin_ratio = data.get('margin_ratio', 1.0)
        liquidation_price = data.get('liquidation_price', 0)
        funding_rate = data.get('funding_rate', 0)
        current_leverage = data.get('current_leverage', 0)

        prompt = f"""🚀 BTC 선물 마진거래 분석 (레버리지 {LEVERAGE}배):

현재상황:
- 가격: ${data['price']:,.0f} ({data['change_24h']:+.1f}%)
- 포지션: {position_size:.4f} BTC (레버리지: {current_leverage:.1f}배)
- 미실현손익: {unrealized_pnl:+.2f}%
- 마진비율: {margin_ratio:.1f}
- 청산가: ${liquidation_price:,.0f}
- 펀딩비율: {funding_rate*10000:+.1f}bps

⚡ 선물 거래 목표:
- 목표수익: {FUTURES_RULES['take_profit']:.1f}%
- 손절기준: {FUTURES_RULES['stop_loss']:.1f}%
- 청산방지: 마진비율 {RISK_MANAGEMENT['margin_ratio_min']:.1f} 이상 유지
- 펀딩효율: 불리한 펀딩 회피

🎯 분석요청:
- 진입/청산 여부
- 포지션 크기 조정
- 리스크 관리 방안

응답형식: {{"action": "buy/sell/close/hold", "reason": "구체적근거", "confidence": 0.8, "leverage": 10, "close_ratio": 0.5}}

즉시 JSON만 응답:"""

        # 3회 재시도
        for attempt in range(3):
            try:
                result = await self._call_anthropic_api(prompt)
                if result:
                    self.call_count += 1
                    self.last_ai_call = datetime.now()

                    # 선물 특화 정보 추가
                    result['ai_call'] = True
                    result['leverage_used'] = current_leverage
                    result['margin_ratio'] = margin_ratio
                    result['attempt'] = attempt + 1

                    logging.info(f"🤖 선물 AI 분석 완료 (호출#{self.call_count})")
                    return result

            except Exception as e:
                logging.warning(f"AI호출 실패 {attempt+1}/3: {e}")
                if attempt < 2:
                    await asyncio.sleep(1)

        # 모든 시도 실패시 긴급 모드
        emergency_action = self._emergency_futures_decision(data)
        logging.error(f"🚨 AI 실패 - 긴급모드: {emergency_action['action']}")
        return emergency_action

    def _emergency_futures_decision(self, data):
        """AI 실패시 긴급 선물 결정"""
        unrealized_pnl = data.get('unrealized_pnl', 0)
        position_size = data.get('position_size', 0)
        margin_ratio = data.get('margin_ratio', 1.0)

        # 포지션이 있고 위험한 상황
        if position_size != 0:
            if unrealized_pnl < -3 or margin_ratio < 0.25:
                return {"action": "close", "reason": "긴급청산_AI실패", "confidence": 0.8, "close_ratio": 1.0}
            elif unrealized_pnl > 2:
                return {"action": "close", "reason": "긴급익절_AI실패", "confidence": 0.7, "close_ratio": 0.5}

        return {"action": "hold", "reason": "긴급대기_AI실패", "confidence": 0.3}

    async def _call_anthropic_api(self, prompt):
        """Anthropic API 호출"""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }

        payload = {
            "model": CLAUDE_MODEL,
            "max_tokens": 200,
            "temperature": 0.1,  # 선물은 더 보수적
            "messages": [{
                "role": "user",
                "content": prompt
            }]
        }

        connector = aiohttp.TCPConnector(
            limit=10,
            keepalive_timeout=15,
            enable_cleanup_closed=True)

        async with aiohttp.ClientSession(connector=connector, timeout=self.timeout) as session:
            async with session.post(self.base_url, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result['content'][0]['text'].strip()
                    return self._parse_futures_response(content)
                else:
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")

    def _parse_futures_response(self, content):
        """선물 응답 파싱"""
        try:
            if '{' in content:
                start = content.find('{')
                end = content.rfind('}') + 1
                json_data = json.loads(content[start:end])

                action = json_data.get('action', 'hold').lower()
                if action in ['buy', 'sell', 'close', 'hold']:
                    return {
                        "action": action,
                        "reason": json_data.get('reason', 'ai_분석')[:50],
                        "confidence": min(json_data.get('confidence', 0.7), 0.95),
                        "leverage": json_data.get('leverage', LEVERAGE),
                        "close_ratio": json_data.get('close_ratio', 1.0)
                    }

        except json.JSONDecodeError:
            pass

        # 텍스트 폴백
        content_lower = content.lower()
        if any(word in content_lower for word in ['청산', 'close', '종료']):
            return {"action": "close", "reason": "텍스트분석_청산", "confidence": 0.6, "close_ratio": 1.0}
        elif any(word in content_lower for word in ['매수', 'buy', '롱']):
            return {"action": "buy", "reason": "텍스트분석_매수", "confidence": 0.6}
        elif any(word in content_lower for word in ['매도', 'sell', '숏']):
            return {"action": "sell", "reason": "텍스트분석_매도", "confidence": 0.6}

        return {"action": "hold", "reason": "파싱실패", "confidence": 0.4}

    def _get_futures_cache(self, data):
        """선물 캐시 확인"""
        # 선물 특화 캐시 키
        price_zone = int(data['price'] / 1000) * 1000
        change_zone = int(data['change_24h'])
        pnl_zone = int(data.get('unrealized_pnl', 0))
        position_key = "long" if data.get('position_size', 0) > 0 else "short" if data.get('position_size', 0) < 0 else "none"
        margin_zone = int(data.get('margin_ratio', 1.0) * 10)

        cache_key = f"fut_{price_zone}_{change_zone}_{pnl_zone}_{position_key}_{margin_zone}"

        cached = self.decision_cache.get(cache_key)
        if cached and self._is_cache_fresh(cached, max_age_minutes=5):  # 선물은 더 짧은 캐시
            return {
                "action": cached['action'],
                "reason": f"{cached['reason']}_캐시",
                "confidence": cached.get('confidence', 0.6) * 0.9
            }

        return None

    def _update_futures_learning(self, market_data, decision):
        """선물 학습 업데이트"""
        self._record_decision(decision)

        # 캐시 업데이트
        price_zone = int(market_data['price'] / 1000) * 1000
        change_zone = int(market_data['change_24h'])
        pnl_zone = int(market_data.get('unrealized_pnl', 0))
        position_key = "long" if market_data.get('position_size', 0) > 0 else "short" if market_data.get('position_size', 0) < 0 else "none"
        margin_zone = int(market_data.get('margin_ratio', 1.0) * 10)

        cache_key = f"fut_{price_zone}_{change_zone}_{pnl_zone}_{position_key}_{margin_zone}"

        self.decision_cache[cache_key] = {
            **decision,
            'cached_at': datetime.now(),
            'market_data': market_data.copy()
        }

        # 캐시 관리
        if len(self.decision_cache) > 100:
            cutoff = datetime.now() - timedelta(minutes=15)
            self.decision_cache = {
                k: v for k, v in self.decision_cache.items()
                if v.get('cached_at', cutoff) > cutoff
            }

    def _record_decision(self, decision):
        """결정 기록"""
        decision_record = {
            **decision,
            'timestamp': datetime.now(),
            'call_number': self.call_count
        }

        self.decisions.append(decision_record)

        if len(self.decisions) > 200:
            self.decisions = self.decisions[-100:]

    def _is_cache_fresh(self, cached_item, max_age_minutes=5):
        """캐시 신선도 체크"""
        if 'cached_at' not in cached_item:
            return False

        age = datetime.now() - cached_item['cached_at']
        return age < timedelta(minutes=max_age_minutes)

    def record_trade_result(self, action, profit_pct):
        """거래 결과 기록"""
        if action in ['close', 'sell']:
            if profit_pct > 0:
                self.win_count += 1
            self.total_profit += profit_pct

    def get_performance_stats(self):
        """성능 통계"""
        if not self.decisions:
            return {'win_rate': 0, 'avg_profit': 0, 'total_calls': 0, 'liquidation_warnings': 0}

        close_decisions = [d for d in self.decisions if d.get('action') in ['close', 'sell']]
        total_decisions = len(self.decisions)

        win_rate = (self.win_count / max(len(close_decisions), 1)) * 100
        avg_profit = self.total_profit / max(len(close_decisions), 1)

        return {
            'win_rate': min(win_rate, 100),
            'avg_profit': avg_profit,
            'total_calls': self.call_count,
            'total_decisions': total_decisions,
            'liquidation_warnings': self.liquidation_warnings,
            'cache_size': len(self.decision_cache)
        }
