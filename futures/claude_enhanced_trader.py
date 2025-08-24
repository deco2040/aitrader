
from claude_market_intelligence import ClaudeMarketIntelligence, MarketDataCollector
from futures_claude_client import FuturesClaudeClient
from futures_mcp_client import FuturesMCPClient
from futures_config import *
import json
import time
from datetime import datetime

class ClaudeEnhancedTrader:
    """
    Claude Sonnet 4의 고급 분석 능력을 활용한 차별화된 트레이딩 시스템
    """
    
    def __init__(self, claude_api_key: str, mcp_client: FuturesMCPClient):
        self.intelligence = ClaudeMarketIntelligence(claude_api_key)
        self.data_collector = MarketDataCollector()
        self.mcp_client = mcp_client
        self.last_analysis_time = 0
        self.market_memory = []  # Claude의 지속적 학습을 위한 메모리
        
    def get_intelligent_trading_signal(self, symbol: str) -> dict:
        """
        Claude의 종합적 분석을 바탕으로 한 트레이딩 신호
        """
        print(f"🧠 Claude 고급 분석 시작: {symbol}")
        
        # 1. 다양한 데이터 수집
        market_data = self._collect_comprehensive_data(symbol)
        
        # 2. Claude 종합 분석
        market_analysis = self.intelligence.analyze_market_context(
            symbol=symbol,
            price_data=market_data['price'],
            news_data=market_data['news']
        )
        
        # 3. 소셜 감정 분석
        social_analysis = self.intelligence.analyze_social_sentiment(
            market_data['social']
        )
        
        # 4. 변동성 예측
        volatility_prediction = self.intelligence.predict_volatility_events(
            market_data['historical'],
            market_data['upcoming_events']
        )
        
        # 5. 종합 판단
        comprehensive_signal = self._synthesize_analysis(
            market_analysis, social_analysis, volatility_prediction
        )
        
        # 6. 메모리에 저장 (Claude의 지속적 학습)
        self._update_market_memory(symbol, comprehensive_signal)
        
        return comprehensive_signal
    
    def _collect_comprehensive_data(self, symbol: str) -> dict:
        """
        종합적인 시장 데이터 수집
        """
        return {
            'price': self._get_current_price_data(symbol),
            'news': self.data_collector.collect_news_data(symbol),
            'social': self.data_collector.collect_social_data(symbol),
            'historical': self._get_historical_data(symbol),
            'upcoming_events': self.data_collector.collect_economic_calendar()
        }
    
    def _get_current_price_data(self, symbol: str) -> dict:
        """
        현재 가격 및 기본 지표 데이터
        """
        # 실제 구현에서는 MCP 클라이언트에서 데이터 가져오기
        return {
            "current_price": 45000,
            "24h_change": 2.5,
            "volume": 1500000000,
            "market_cap": 850000000000,
            "fear_greed_index": 75
        }
    
    def _get_historical_data(self, symbol: str) -> list:
        """
        과거 데이터 (Claude 패턴 분석용)
        """
        # 실제로는 더 많은 데이터 포인트
        return [
            {"timestamp": "2024-01-01", "price": 42000, "volume": 1000000},
            {"timestamp": "2024-01-02", "price": 43000, "volume": 1200000},
            # ... 더 많은 데이터
        ]
    
    def _synthesize_analysis(self, market_analysis: dict, social_analysis: dict, 
                           volatility_prediction: dict) -> dict:
        """
        Claude의 다차원 분석 결과를 종합
        """
        # Claude의 종합 판단을 위한 메타 분석
        synthesis_prompt = f"""
        TRADING SYSTEM: 24-hour automated futures trading targeting 0.5% daily profit
        RISK PARAMETERS: Maximum 20% drawdown tolerance, intelligent liquidation management
        APPROACH: Aggressive but calculated, position splitting for risk control
        
        Synthesize the following analysis for final trading decision:
        
        Market Analysis: {json.dumps(market_analysis, indent=2)}
        Social Sentiment: {json.dumps(social_analysis, indent=2)}
        Volatility Prediction: {json.dumps(volatility_prediction, indent=2)}
        
        Make the final trading decision considering:
        - Can we achieve 0.1-0.3% profit in next 2-6 hours?
        - Should we split positions (3-5 entries) or go with single large position?
        - Current liquidation distance vs profit potential
        - Optimal position size to stay within 20% risk while maximizing profit
        
        Final Decision JSON:
        {{
            "action": "aggressive_long/moderate_long/scalp_long/wait_for_setup/scalp_short/moderate_short/aggressive_short",
            "confidence": 0-100,
            "total_position_allocation": 0.1-1.0,
            "entry_strategy": {{
                "type": "single/split_3/split_5/dca",
                "first_entry": 0.3-0.6,
                "second_entry": 0.2-0.4,
                "third_entry": 0.1-0.3
            }},
            "stop_loss_tight": "price for quick scalps",
            "stop_loss_wide": "price for swing positions", 
            "take_profit_targets": {{
                "tp1": "price (0.1-0.2% profit)",
                "tp2": "price (0.3-0.5% profit)",
                "tp3": "price (0.8-1.2% profit)"
            }},
            "max_hold_time": "15min/1h/4h/12h",
            "leverage_usage": 5-20,
            "liquidation_buffer": "percentage distance to liquidation",
            "reasoning": "detailed justification focusing on profit probability and risk management",
            "profit_expectation": "expected percentage gain in specified timeframe",
            "risk_factors": ["factor1", "factor2"],
            "exit_conditions": ["condition1", "condition2"],
            "session_preference": "asia/europe/us/any",
            "funding_strategy": "hold_through/exit_before"
        }}
        """
        
        try:
            response = self.intelligence.client.messages.create(
                model=self.intelligence.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": synthesis_prompt}]
            )
            
            final_decision = json.loads(response.content[0].text)
            
            # 추가 안전 검증
            final_decision = self._apply_safety_checks(final_decision)
            
            return final_decision
            
        except Exception as e:
            print(f"종합 분석 오류: {e}")
            return {"action": "hold", "confidence": 0, "reasoning": f"분석 오류: {e}"}
    
    def _apply_safety_checks(self, decision: dict) -> dict:
        """
        Safety validation for aggressive but controlled trading
        Target: 0.5% daily profit, Max risk: 20% drawdown
        """
        # 1. Confidence threshold for aggressive system (lower threshold for more trades)
        if decision.get('confidence', 0) < 45:
            decision['action'] = 'wait_for_setup'
            decision['reasoning'] += " (Low confidence - waiting for better setup)"
        
        # 2. Position allocation limits (allow up to 100% for calculated risks)
        max_allocation = min(decision.get('total_position_allocation', 0.3), 1.0)
        decision['total_position_allocation'] = max_allocation
        
        # 3. Leverage safety (max 20x, optimal 10-15x for daily 0.5% target)
        max_leverage = min(decision.get('leverage_usage', 10), 20)
        decision['leverage_usage'] = max_leverage
        
        # 4. Liquidation buffer enforcement (minimum 25% buffer from liquidation)
        min_liquidation_buffer = 25.0
        current_buffer = decision.get('liquidation_buffer', '30%')
        if isinstance(current_buffer, str):
            buffer_value = float(current_buffer.replace('%', ''))
            if buffer_value < min_liquidation_buffer:
                decision['total_position_allocation'] *= 0.7  # Reduce position size
                decision['reasoning'] += f" (Position reduced - liquidation too close: {buffer_value}%)"
        
        # 5. Maximum risk per trade (ensure single trade can't cause >20% loss)
        max_single_trade_risk = 5.0  # 5% per trade max
        leverage = decision.get('leverage_usage', 10)
        position_size = decision.get('total_position_allocation', 0.3)
        potential_loss = leverage * position_size * 100  # Max % loss if position goes to 0
        
        if potential_loss > max_single_trade_risk:
            reduction_factor = max_single_trade_risk / potential_loss
            decision['total_position_allocation'] *= reduction_factor
            decision['reasoning'] += f" (Position reduced for risk management: {potential_loss:.1f}% risk)"
        
        # 6. Mandatory stop loss (but allow wider stops for swing trades)
        if 'stop_loss_tight' not in decision and 'stop_loss_wide' not in decision:
            decision['stop_loss_tight'] = "MANDATORY - set based on current price"
            decision['stop_loss_wide'] = "MANDATORY - set based on current price"
        
        # 7. Take profit enforcement (ensure we lock in profits)
        if 'take_profit_targets' not in decision:
            decision['take_profit_targets'] = {
                "tp1": "0.1-0.2% profit - MANDATORY",
                "tp2": "0.3-0.5% profit - MANDATORY", 
                "tp3": "0.8-1.2% profit - OPTIONAL"
            }
        
        return decision
    
    def _update_market_memory(self, symbol: str, analysis: dict):
        """
        Claude의 지속적 학습을 위한 메모리 업데이트
        """
        memory_entry = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "analysis": analysis,
            "market_conditions": self._get_current_market_state()
        }
        
        self.market_memory.append(memory_entry)
        
        # 메모리 크기 제한 (최근 100개만 유지)
        if len(self.market_memory) > 100:
            self.market_memory = self.market_memory[-100:]
    
    def _get_current_market_state(self) -> dict:
        """
        현재 시장 상태 스냅샷
        """
        return {
            "time": datetime.now().hour,
            "day_of_week": datetime.now().weekday(),
            "market_session": self._get_market_session(),
            "volatility_level": "high"  # 실제로는 계산
        }
    
    def _get_market_session(self) -> str:
        """
        현재 시장 세션 판단
        """
        hour = datetime.now().hour
        if 0 <= hour < 8:
            return "asia"
        elif 8 <= hour < 16:
            return "europe"
        else:
            return "america"
    
    def get_market_narrative(self, symbol: str) -> str:
        """
        Claude가 생성하는 시장 해석 스토리
        """
        market_data = self._collect_comprehensive_data(symbol)
        narrative = self.intelligence.generate_narrative_analysis(market_data)
        return narrative
    
    def execute_intelligent_trade(self, symbol: str) -> dict:
        """
        Claude 분석 기반 실제 거래 실행
        """
        # 1. Claude 분석 수행
        signal = self.get_intelligent_trading_signal(symbol)
        
        # 2. 시장 스토리 생성
        narrative = self.get_market_narrative(symbol)
        
        print(f"📊 Claude 분석 결과:")
        print(f"행동: {signal.get('action')}")
        print(f"신뢰도: {signal.get('confidence')}%")
        print(f"근거: {signal.get('reasoning')}")
        print(f"\n📖 시장 해석:")
        print(narrative)
        
        # 3. 실제 거래 실행
        if signal['action'] in ['buy', 'strong_buy']:
            result = self._execute_buy_order(symbol, signal)
        elif signal['action'] in ['sell', 'strong_sell']:
            result = self._execute_sell_order(symbol, signal)
        else:
            result = {"action": "hold", "message": "거래 조건 미충족"}
        
        return {
            "claude_analysis": signal,
            "market_narrative": narrative,
            "execution_result": result
        }
    
    def _execute_buy_order(self, symbol: str, signal: dict) -> dict:
        """
        매수 주문 실행
        """
        try:
            position_size = signal.get('position_size', 0.1) * POSITION_SIZE
            success = self.mcp_client.execute_buy_order(symbol, position_size)
            
            return {
                "action": "buy",
                "amount": position_size,
                "success": success,
                "stop_loss": signal.get('stop_loss'),
                "take_profit": signal.get('take_profit')
            }
        except Exception as e:
            return {"action": "buy", "success": False, "error": str(e)}
    
    def _execute_sell_order(self, symbol: str, signal: dict) -> dict:
        """
        매도 주문 실행
        """
        try:
            # 현재 포지션 확인 후 매도
            current_position = self.mcp_client.get_position(symbol)
            if current_position and current_position.get("size", 0) > 0:
                success = self.mcp_client.execute_sell_order(symbol, current_position["size"])
                return {
                    "action": "sell",
                    "amount": current_position["size"],
                    "success": success
                }
            else:
                return {"action": "sell", "success": False, "message": "매도할 포지션 없음"}
        except Exception as e:
            return {"action": "sell", "success": False, "error": str(e)}

# 사용 예시
if __name__ == "__main__":
    # 더미 MCP 클라이언트 (테스트용)
    class DummyMCPClient:
        def execute_buy_order(self, symbol, amount):
            print(f"매수 주문: {symbol}, 수량: {amount}")
            return True
        
        def execute_sell_order(self, symbol, amount):
            print(f"매도 주문: {symbol}, 수량: {amount}")
            return True
        
        def get_position(self, symbol):
            return {"symbol": symbol, "size": 100}
    
    # Claude Enhanced Trader 테스트
    trader = ClaudeEnhancedTrader(
        claude_api_key="your_claude_api_key",
        mcp_client=DummyMCPClient()
    )
    
    # 지능적 거래 실행
    result = trader.execute_intelligent_trade("BTC/USDT")
    print(f"\n최종 결과: {json.dumps(result, indent=2, ensure_ascii=False)}")
