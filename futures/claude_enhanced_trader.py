import anthropic
from .claude_market_intelligence import ClaudeMarketIntelligence, MarketDataCollector
from .futures_claude_client import FuturesClaudeClient
from .futures_mcp_client import FuturesMCPClient
from .futures_config import *
import json
import time
from datetime import datetime

class ClaudeEnhancedTrader:
    """
    Claude AI Enhanced Trading System
    """

    def __init__(self, claude_api_key: str):
        self.claude_api_key = claude_api_key
        self.claude_client = anthropic.Anthropic(api_key=claude_api_key)
        self.market_intelligence = ClaudeMarketIntelligence(claude_api_key)

    def analyze_market_with_claude(self, symbol: str) -> dict:
        """
        Claude를 사용한 시장 분석
        """
        try:
            # 시장 데이터 수집
            market_context = self._gather_market_context(symbol)

            # Claude에게 분석 요청
            prompt = self._create_analysis_prompt(symbol, market_context)

            message = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # 응답 파싱
            analysis = self._parse_claude_response(message.content[0].text)
            return analysis

        except Exception as e:
            print(f"Claude 분석 오류: {e}")
            return {
                'action': 'HOLD',
                'confidence': 0,
                'reasoning': f'분석 중 오류 발생: {str(e)}'
            }

    def _gather_market_context(self, symbol: str) -> dict:
        """
        시장 컨텍스트 수집
        """
        return {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'price': 45000,  # 더미 데이터
            'volume': 1000000,
            'trend': 'bullish'
        }

    def _create_analysis_prompt(self, symbol: str, context: dict) -> str:
        """
        Claude 분석 프롬프트 생성
        """
        return f"""
당신은 전문적인 암호화폐 선물 거래 분석가입니다.

현재 시장 상황:
- 심볼: {symbol}
- 현재가: ${context.get('price', 'N/A')}
- 거래량: {context.get('volume', 'N/A')}
- 시간: {context.get('timestamp', 'N/A')}

다음 형식으로 분석 결과를 제공해주세요:

분석결과:
- 행동: [BUY/SELL/HOLD]
- 신뢰도: [0-100]
- 근거: [상세한 분석 근거]

현재 시장 상황을 고려하여 최적의 거래 전략을 제시해주세요.
"""

    def _parse_claude_response(self, response: str) -> dict:
        """
        Claude 응답 파싱
        """
        try:
            # 간단한 파싱 로직
            lines = response.split('\n')
            action = 'HOLD'
            confidence = 50
            reasoning = response

            for line in lines:
                if '행동:' in line or 'Action:' in line:
                    if 'BUY' in line.upper():
                        action = 'BUY'
                    elif 'SELL' in line.upper():
                        action = 'SELL'
                elif '신뢰도:' in line or 'Confidence:' in line:
                    try:
                        confidence = int(''.join(filter(str.isdigit, line)))
                    except:
                        confidence = 50

            return {
                'action': action,
                'confidence': confidence,
                'reasoning': reasoning
            }

        except Exception as e:
            return {
                'action': 'HOLD',
                'confidence': 0,
                'reasoning': f'응답 파싱 오류: {str(e)}'
            }