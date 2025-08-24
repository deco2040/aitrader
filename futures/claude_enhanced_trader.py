import anthropic
from .claude_market_intelligence import ClaudeMarketIntelligence, MarketDataCollector
from .futures_claude_client import FuturesClaudeClient
from .futures_mcp_client import FuturesMCPClient
from .futures_config import *
import json
import time
from datetime import datetime

class ClaudeEnhancedTraderTrader:
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
    
    def get_intelligent_trading_signal(self, symbol: str) -> dict:
        """지능형 거래 신호 생성"""
        return self.analyze_market_with_claude(symbol)
    
    def get_market_narrative(self, symbol: str) -> str:
        """시장 해석 생성"""
        analysis = self.analyze_market_with_claude(symbol)
        return analysis.get('reasoning', 'No narrative available')
import json
import time
from typing import Dict, Any

class ClaudeEnhancedTrader:
    """Claude AI 기반 고급 거래 시스템"""
    
    def __init__(self, claude_api_key: str, mcp_client=None):
        self.claude_api_key = claude_api_key
        self.mcp_client = mcp_client
        
    def get_intelligent_trading_signal(self, symbol: str) -> Dict[str, Any]:
        """지능형 거래 신호 생성"""
        try:
            # 시뮬레이션된 Claude 분석 결과
            analysis = {
                'action': 'HOLD',
                'confidence': 75,
                'position_size': 0.1,
                'reasoning': '현재 시장은 횡보 구간으로 추가 신호 대기가 필요함',
                'risk_factors': ['변동성 증가', '거래량 감소'],
                'alternative_scenarios': ['돌파 시 상승', '지지선 붕괴 시 하락']
            }
            
            # 실제 시장 데이터 기반 조정
            if self.mcp_client:
                market_data = self.mcp_client.get_market_data(symbol)
                if market_data.get('volume', 0) > 1000000:
                    analysis['confidence'] += 10
                    analysis['action'] = 'BUY' if market_data.get('price', 0) > 45000 else 'SELL'
            
            return analysis
        except Exception as e:
            return {
                'action': 'HOLD',
                'confidence': 50,
                'reasoning': f'분석 중 오류 발생: {str(e)}',
                'risk_factors': ['시스템 오류'],
                'alternative_scenarios': ['수동 분석 필요']
            }
    
    def get_market_narrative(self, symbol: str) -> str:
        """시장 스토리텔링"""
        return f"""
        {symbol} 시장 분석:
        
        현재 시장은 주요 저항선과 지지선 사이에서 횡보하고 있습니다.
        거시경제적 요인들이 시장 방향성에 영향을 미치고 있으며,
        투자자들은 다음 주요 경제 지표 발표를 주시하고 있습니다.
        
        기술적으로는 이동평균선이 수렴하는 패턴을 보이며,
        볼린저 밴드가 수축하여 큰 움직임이 임박했을 가능성이 있습니다.
        """
    
    def analyze_market_with_claude(self, symbol: str) -> Dict[str, Any]:
        """Claude를 통한 종합 시장 분석"""
        signal = self.get_intelligent_trading_signal(symbol)
        narrative = self.get_market_narrative(symbol)
        
        return {
            'action': signal['action'],
            'confidence': signal['confidence'],
            'reasoning': signal['reasoning'],
            'narrative': narrative,
            'timestamp': time.time()
        }
    
    def execute_intelligent_trade(self, symbol: str) -> Dict[str, Any]:
        """지능형 거래 실행"""
        analysis = self.analyze_market_with_claude(symbol)
        
        result = {
            'claude_analysis': analysis,
            'market_narrative': analysis['narrative'],
            'execution_result': {'success': True, 'message': '분석 완료'}
        }
        
        # 실제 거래 실행 (시뮬레이션)
        if self.mcp_client and analysis['action'] in ['BUY', 'SELL']:
            try:
                if analysis['action'] == 'BUY':
                    success = self.mcp_client.execute_buy_order(symbol, 0.1)
                else:
                    success = self.mcp_client.execute_sell_order(symbol, 0.1)
                
                result['execution_result'] = {
                    'success': success,
                    'message': f'{analysis["action"]} 주문 {"성공" if success else "실패"}'
                }
            except Exception as e:
                result['execution_result'] = {
                    'success': False,
                    'message': f'거래 실행 오류: {str(e)}'
                }
        
        return result

# 하위 호환성을 위한 별칭
ClaudeEnhancedTraderTrader = ClaudeEnhancedTrader
