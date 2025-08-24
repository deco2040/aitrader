import json
from datetime import datetime
from typing import Dict, Any

class ClaudeEnhancedTrader:
    """
    Claude AI를 활용한 고급 거래 시스템
    """

    def __init__(self, claude_api_key: str, mcp_client):
        self.claude_api_key = claude_api_key
        self.mcp_client = mcp_client
        self.market_intelligence = {}

    def get_intelligent_trading_signal(self, symbol: str) -> Dict[str, Any]:
        """
        Claude AI를 활용한 지능형 거래 신호 생성
        """
        try:
            # 시장 데이터 수집
            market_data = self.mcp_client.get_market_data(symbol)
            position = self.mcp_client.get_position(symbol)

            # 간단한 규칙 기반 분석 (실제로는 Claude API 호출)
            price = market_data.get('price', 45000)
            change_24h = market_data.get('24h_change', 0)

            # 기본 신호 로직
            if change_24h > 5:
                action = "SELL"
                confidence = 75
                reasoning = "24시간 상승률이 5%를 초과하여 과매수 구간"
            elif change_24h < -5:
                action = "BUY"
                confidence = 80
                reasoning = "24시간 하락률이 5%를 초과하여 과매도 구간"
            else:
                action = "HOLD"
                confidence = 60
                reasoning = "시장이 중립적 상태로 관망 추천"

            return {
                "action": action,
                "confidence": confidence,
                "reasoning": reasoning,
                "market_sentiment": "neutral",
                "risk_level": "medium",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "action": "HOLD",
                "confidence": 0,
                "reasoning": f"분석 중 오류 발생: {str(e)}",
                "error": True
            }

    def get_market_narrative(self, symbol: str) -> str:
        """
        시장 상황에 대한 스토리텔링 기반 해석
        """
        try:
            market_data = self.mcp_client.get_market_data(symbol)
            signal = self.get_intelligent_trading_signal(symbol)

            narrative = f"""
📊 {symbol} 시장 인텔리전스 보고서

현재 {symbol}은 ${market_data.get('price', 45000):,.0f}에 거래되고 있으며, 
지난 24시간 동안 {market_data.get('24h_change', 0):+.1f}% 변동했습니다.

🧠 AI 분석 결과:
- 추천 행동: {signal.get('action', 'N/A')}
- 신뢰도: {signal.get('confidence', 0)}%
- 근거: {signal.get('reasoning', 'N/A')}

💡 투자 관점: {signal.get('market_sentiment', 'neutral')} 시장 상황에서 
{signal.get('risk_level', 'medium')} 위험도의 접근이 필요합니다.
"""
            return narrative

        except Exception as e:
            return f"시장 해석 생성 중 오류 발생: {str(e)}"

    def execute_intelligent_trade(self, symbol: str) -> Dict[str, Any]:
        """
        지능형 거래 실행
        """
        try:
            # 신호 생성
            signal = self.get_intelligent_trading_signal(symbol)
            market_narrative = self.get_market_narrative(symbol)

            # 거래 실행
            execution_result = {"executed": False, "reason": "No action needed"}

            if signal["action"] == "BUY" and signal["confidence"] > 70:
                success = self.mcp_client.execute_buy_order(symbol, 0.1)
                execution_result = {
                    "executed": success,
                    "action": "BUY",
                    "amount": 0.1,
                    "reason": "High confidence buy signal"
                }
            elif signal["action"] == "SELL" and signal["confidence"] > 70:
                success = self.mcp_client.execute_sell_order(symbol, 0.1)
                execution_result = {
                    "executed": success,
                    "action": "SELL", 
                    "amount": 0.1,
                    "reason": "High confidence sell signal"
                }

            return {
                "claude_analysis": signal,
                "market_narrative": market_narrative,
                "execution_result": execution_result
            }

        except Exception as e:
            return {
                "claude_analysis": {"error": str(e)},
                "market_narrative": f"오류: {str(e)}",
                "execution_result": {"executed": False, "error": str(e)}
            }