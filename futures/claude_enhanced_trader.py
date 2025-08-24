` tags.

<replit_final_file>
import json
from datetime import datetime
from typing import Dict, Any, Optional

class ClaudeEnhancedTrader:
    """Claude AI 향상된 거래자"""

    def __init__(self, claude_api_key: str, mcp_client):
        self.claude_api_key = claude_api_key
        self.mcp_client = mcp_client
        self.analysis_history = []

    def get_intelligent_trading_signal(self, symbol: str) -> Dict[str, Any]:
        """지능형 거래 신호 생성"""
        try:
            # 시장 데이터 수집
            market_data = self.mcp_client.get_market_data(symbol)
            position_info = self.mcp_client.get_position(symbol)

            # 기본 분석
            price = market_data.get('price', 50000)
            volume = market_data.get('volume', 1000)

            # 간단한 신호 로직
            if price > 45000:
                action = "BUY"
                confidence = 75
            elif price < 40000:
                action = "SELL"
                confidence = 80
            else:
                action = "HOLD"
                confidence = 60

            signal = {
                'symbol': symbol,
                'action': action,
                'confidence': confidence,
                'price': price,
                'volume': volume,
                'timestamp': datetime.now().isoformat(),
                'reasoning': f"Price analysis based on {price} level"
            }

            self.analysis_history.append(signal)
            return signal

        except Exception as e:
            print(f"Signal generation error: {e}")
            return {
                'symbol': symbol,
                'action': 'HOLD',
                'confidence': 0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def get_market_narrative(self, symbol: str) -> str:
        """시장 해석 생성"""
        try:
            market_data = self.mcp_client.get_market_data(symbol)
            price = market_data.get('price', 50000)

            narrative = f"""
            Market Analysis for {symbol}:

            Current Price: ${price:,.2f}
            Market Sentiment: {'Bullish' if price > 45000 else 'Bearish'}

            Technical Analysis:
            - The price is {'above' if price > 45000 else 'below'} key resistance levels
            - Volume indicates {'strong' if price > 50000 else 'moderate'} market interest

            Recommendation: {'Consider buying on dips' if price > 45000 else 'Wait for better entry points'}
            """

            return narrative.strip()

        except Exception as e:
            return f"Market narrative generation failed: {e}"

    def analyze_risk_reward(self, symbol: str, position_size: float) -> Dict[str, Any]:
        """리스크/수익 분석"""
        try:
            market_data = self.mcp_client.get_market_data(symbol)
            price = market_data.get('price', 50000)

            # 간단한 리스크 계산
            stop_loss = price * 0.95  # 5% 손절
            take_profit = price * 1.10  # 10% 익절

            risk_amount = position_size * (price - stop_loss)
            reward_amount = position_size * (take_profit - price)

            return {
                'entry_price': price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'risk_amount': risk_amount,
                'reward_amount': reward_amount,
                'risk_reward_ratio': reward_amount / risk_amount if risk_amount > 0 else 0,
                'recommendation': 'FAVORABLE' if reward_amount > risk_amount * 2 else 'CAUTION'
            }

        except Exception as e:
            return {'error': str(e)}

    def get_analysis_history(self) -> list:
        """분석 기록 반환"""
        return self.analysis_history