
import random
import time
from typing import Dict, Any
import json

class ClaudeEnhancedTrader:
    """
    Claude AI를 활용한 고급 선물 거래 시스템
    실제 Claude API 연결이 필요하지만 여기서는 시뮬레이션으로 구현
    """
    
    def __init__(self, claude_api_key: str, mcp_client):
        self.claude_api_key = claude_api_key
        self.mcp_client = mcp_client
        print(f"ClaudeEnhancedTrader initialized with API key: {claude_api_key[:10]}...")
    
    def get_intelligent_trading_signal(self, symbol: str) -> Dict[str, Any]:
        """Claude를 활용한 지능형 거래 신호 생성"""
        try:
            # 시장 데이터 수집
            market_data = self.mcp_client.get_market_data(symbol)
            position = self.mcp_client.get_position(symbol)
            balance = self.mcp_client.get_account_balance()
            
            # Claude 분석 시뮬레이션
            actions = ["BUY", "SELL", "HOLD"]
            action = random.choice(actions)
            confidence = random.randint(60, 95)
            
            # 더 정교한 분석 결과
            analysis = {
                "action": action,
                "confidence": confidence,
                "reasoning": self._generate_reasoning(symbol, market_data, action),
                "risk_level": "LOW" if confidence > 80 else "MEDIUM",
                "position_size_recommendation": self._calculate_position_size(balance, confidence),
                "stop_loss": market_data["price"] * 0.95 if action == "BUY" else market_data["price"] * 1.05,
                "take_profit": market_data["price"] * 1.08 if action == "BUY" else market_data["price"] * 0.92,
                "market_sentiment": random.choice(["BULLISH", "BEARISH", "NEUTRAL"]),
                "volatility_assessment": random.choice(["HIGH", "MEDIUM", "LOW"]),
                "news_impact": random.choice(["POSITIVE", "NEGATIVE", "NEUTRAL"])
            }
            
            return analysis
            
        except Exception as e:
            print(f"지능형 신호 생성 오류: {e}")
            return {
                "action": "HOLD",
                "confidence": 0,
                "reasoning": f"분석 오류: {str(e)}",
                "risk_level": "HIGH"
            }
    
    def get_market_narrative(self, symbol: str) -> str:
        """Claude를 활용한 시장 해석 스토리"""
        try:
            market_data = self.mcp_client.get_market_data(symbol)
            price = market_data["price"]
            volume = market_data["volume"]
            change = market_data.get("change_24h", 0)
            
            # 시장 상황에 따른 내러티브 생성
            if change > 0.03:
                sentiment = "강세"
                narrative = f"""
🚀 {symbol} 강력한 상승 모멘텀

현재 {symbol}은 ${price:,.0f}에서 거래되고 있으며, 24시간 동안 {change*100:.1f}% 상승했습니다.
거래량 {volume:,}은 평균보다 높아 시장 참여자들의 적극적인 관심을 보여줍니다.

주요 관찰 포인트:
- 기술적 저항선을 돌파하며 상승 트렌드 지속
- 거래량 증가로 상승 모멘텀 신뢰도 높음
- 다음 목표가: ${price * 1.08:,.0f}
- 지지선: ${price * 0.95:,.0f}

추천: 분할 매수 전략으로 접근, 손절매 설정 필수
"""
            elif change < -0.03:
                sentiment = "약세"
                narrative = f"""
📉 {symbol} 조정 국면 진입

{symbol}이 ${price:,.0f}로 하락하며 24시간 동안 {abs(change)*100:.1f}% 하락했습니다.
이는 건전한 조정으로 해석될 수 있으나 추가 하락 리스크에 주의가 필요합니다.

주요 관찰 포인트:
- 기술적 지지선 테스트 중
- 거래량 패턴으로 바닥 신호 모니터링 필요
- 잠재적 반등 구간: ${price * 1.05:,.0f}
- 추가 하락시 지지선: ${price * 0.92:,.0f}

추천: 관망 후 바닥 확인되면 분할 매수 고려
"""
            else:
                sentiment = "중립"
                narrative = f"""
⚖️ {symbol} 횡보 구간에서 방향성 모색

{symbol}은 현재 ${price:,.0f} 근처에서 제한적 움직임을 보이고 있습니다.
시장은 다음 방향성을 결정하기 위한 에너지를 축적하는 것으로 보입니다.

주요 관찰 포인트:
- 좁은 가격대에서 거래량 감소
- 돌파 또는 하락 신호 대기 중
- 상방 저항: ${price * 1.03:,.0f}
- 하방 지지: ${price * 0.97:,.0f}

추천: 명확한 방향성 확인될 때까지 관망 권장
"""
            
            return narrative.strip()
            
        except Exception as e:
            return f"시장 해석 생성 오류: {str(e)}"
    
    def execute_intelligent_trade(self, symbol: str) -> Dict[str, Any]:
        """지능형 거래 실행"""
        try:
            # 지능형 분석 수행
            claude_analysis = self.get_intelligent_trading_signal(symbol)
            market_narrative = self.get_market_narrative(symbol)
            
            # 거래 실행 결정
            execution_result = {"executed": False, "reason": ""}
            
            if claude_analysis["confidence"] > 75:
                action = claude_analysis["action"]
                
                if action == "BUY":
                    amount = claude_analysis["position_size_recommendation"]
                    success = self.mcp_client.execute_buy_order(symbol, amount)
                    execution_result = {
                        "executed": success,
                        "action": "BUY",
                        "amount": amount,
                        "reason": "High confidence buy signal"
                    }
                    
                elif action == "SELL":
                    position = self.mcp_client.get_position(symbol)
                    if position["size"] > 0:
                        amount = min(position["size"], claude_analysis["position_size_recommendation"])
                        success = self.mcp_client.execute_sell_order(symbol, amount)
                        execution_result = {
                            "executed": success,
                            "action": "SELL", 
                            "amount": amount,
                            "reason": "High confidence sell signal"
                        }
                    else:
                        execution_result = {
                            "executed": False,
                            "reason": "No position to sell"
                        }
                        
                else:  # HOLD
                    execution_result = {
                        "executed": False,
                        "action": "HOLD",
                        "reason": "Analysis recommends holding"
                    }
            else:
                execution_result = {
                    "executed": False,
                    "reason": f"Confidence too low: {claude_analysis['confidence']}%"
                }
            
            return {
                "claude_analysis": claude_analysis,
                "market_narrative": market_narrative,
                "execution_result": execution_result
            }
            
        except Exception as e:
            return {
                "claude_analysis": {"action": "HOLD", "confidence": 0, "reasoning": f"Error: {e}"},
                "market_narrative": f"Analysis failed: {str(e)}",
                "execution_result": {"executed": False, "reason": f"System error: {e}"}
            }
    
    def _generate_reasoning(self, symbol: str, market_data: Dict, action: str) -> str:
        """거래 결정 근거 생성"""
        reasonings = {
            "BUY": [
                f"{symbol} 기술적 지표가 강세 신호를 보임",
                f"거래량 증가와 함께 상승 모멘텀 감지",
                f"시장 센티먼트 개선으로 매수 기회 포착",
                f"지지선에서 반등 패턴 확인"
            ],
            "SELL": [
                f"{symbol} 과매수 구간 진입으로 조정 예상",
                f"저항선 근처에서 매도 압력 증가",
                f"리스크 관리 차원에서 일부 수익 실현",
                f"시장 불확실성 증가로 포지션 축소"
            ],
            "HOLD": [
                f"{symbol} 현재 명확한 방향성 부재",
                f"시장 상황 관찰 필요한 구간",
                f"추가 신호 대기 중인 상황",
                f"리스크 대비 수익 비율 불충분"
            ]
        }
        
        return random.choice(reasonings.get(action, ["일반적인 시장 분석 기준"]))
    
    def _calculate_position_size(self, balance: Dict, confidence: int) -> float:
        """신뢰도 기반 포지션 크기 계산"""
        available = balance.get("available", 1000)
        base_size = available * 0.1  # 기본 10%
        
        # 신뢰도에 따른 조정
        confidence_multiplier = confidence / 100
        position_size = base_size * confidence_multiplier
        
        # 최대 30%로 제한
        max_size = available * 0.3
        return min(position_size, max_size)
