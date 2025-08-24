
import json
import requests
from datetime import datetime, timedelta
import anthropic
from futures_config import *

class ClaudeMarketIntelligence:
    """
    Claude Sonnet 4를 활용한 고급 시장 분석 시스템
    - 뉴스/소셜 감정 분석
    - 거시경제 맥락 이해
    - 패턴 인식 및 예측
    - 멀티모달 차트 분석
    """
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
        
    def analyze_market_context(self, symbol: str, price_data: dict, news_data: list) -> dict:
        """
        Claude를 활용한 종합적 시장 맥락 분석
        """
        prompt = f"""
        You are an elite cryptocurrency futures trader and market analyst operating a 24-hour automated trading system.
        
        TARGET: 0.5% daily profit through strategic position splitting and calculated risk-taking.
        RISK TOLERANCE: Maximum 20% drawdown allowed - aggressive but controlled.
        PHILOSOPHY: Embrace calculated risks, don't fear liquidation, but manage it intelligently.
        
        Analyze the current {symbol} market situation:
        
        Price Data:
        {json.dumps(price_data, indent=2)}
        
        Recent News:
        {json.dumps(news_data, indent=2)}
        
        ANALYZE THE DATA STEP-BY-STEP:
        
        STEP 1: PRICE ACTION ANALYSIS
        - Current price trend (1h, 4h, 12h timeframes)
        - Support/resistance levels identification
        - Volume profile analysis
        - Price momentum indicators (RSI, MACD divergences)
        
        STEP 2: MARKET STRUCTURE EVALUATION
        - Market phase identification (accumulation/distribution/trending)
        - Order book analysis (bid/ask imbalances)
        - Funding rate implications
        - Open interest changes
        
        STEP 3: NEWS & SENTIMENT IMPACT ASSESSMENT
        - News sentiment scoring (-100 to +100)
        - Social media sentiment analysis
        - Correlation with price movements
        - Expected impact duration (1h/4h/12h/24h+)
        
        STEP 4: VOLATILITY & RISK ANALYSIS
        - Current volatility percentile
        - Expected volatility in next 1-4 hours
        - Liquidation cascade risk assessment
        - Market maker vs retail sentiment
        
        STEP 5: LEVERAGE OPTIMIZATION
        - Calculate optimal leverage based on:
          * Current market volatility
          * Distance to liquidation
          * Account balance utilization
          * Expected move size
        - Dynamic leverage adjustment (5x-20x scale)
        - Risk-per-trade calculation
        
        STEP 6: TIMING ANALYSIS
        - Current market session characteristics
        - Funding time proximity (00:00, 08:00, 16:00 UTC)
        - Optimal entry/exit windows
        - Session transition volatility patterns
        
        STEP 7: POSITION STRATEGY FORMULATION
        - Entry strategy (single/split/DCA approach)
        - Position sizing per entry
        - Stop-loss placement strategy
        - Take-profit ladder setup
        
        STEP 8: REAL-TIME STRATEGY ADAPTATION
        - Market condition changes monitoring
        - Leverage adjustment triggers
        - Position size modification conditions
        - Exit strategy modifications
        
        Provide analysis considering:
        
        1. IMMEDIATE PROFIT OPPORTUNITIES (next 1-4 hours for 0.1-0.3% gains)
        2. POSITION SPLITTING STRATEGY (multiple entries vs single large position)
        3. DYNAMIC LEVERAGE CALCULATION (5x-20x based on market conditions)
        4. LIQUIDATION DISTANCE OPTIMIZATION (minimum 25% buffer)
        5. 24-HOUR MARKET CYCLES (Asia/Europe/US sessions and funding times)
        6. VOLATILITY EXPLOITATION (how to profit from price swings)
        7. RISK-REWARD OPTIMIZATION (targeting 0.5% daily with <20% max loss)
        8. REAL-TIME STRATEGY MODIFICATION (adaptive to changing conditions)
        
        Respond in JSON format:
        {{
            "step_by_step_analysis": {{
                "step1_price_action": {{
                    "trend_1h": "bullish/bearish/neutral",
                    "trend_4h": "bullish/bearish/neutral",
                    "trend_12h": "bullish/bearish/neutral",
                    "support_levels": [price1, price2, price3],
                    "resistance_levels": [price1, price2, price3],
                    "momentum_score": 0-100
                }},
                "step2_market_structure": {{
                    "market_phase": "accumulation/distribution/trending/ranging",
                    "order_book_imbalance": "buy_heavy/sell_heavy/balanced",
                    "funding_rate_impact": "positive/negative/neutral",
                    "open_interest_change": "increasing/decreasing/stable"
                }},
                "step3_news_sentiment": {{
                    "news_sentiment_score": -100 to 100,
                    "social_sentiment_score": -100 to 100,
                    "correlation_strength": 0-100,
                    "impact_duration": "1h/4h/12h/24h+"
                }},
                "step4_volatility_risk": {{
                    "volatility_percentile": 0-100,
                    "expected_volatility_1h": 0-100,
                    "expected_volatility_4h": 0-100,
                    "liquidation_cascade_risk": "low/medium/high/extreme",
                    "market_participant_bias": "retail_heavy/smart_money/balanced"
                }},
                "step5_leverage_optimization": {{
                    "current_market_volatility": 0-100,
                    "optimal_leverage": 5-20,
                    "max_safe_leverage": 5-20,
                    "risk_per_trade": 0-5,
                    "leverage_adjustment_trigger": "volatility_increase/volatility_decrease/trend_change/news_impact"
                }},
                "step6_timing_analysis": {{
                    "current_session": "asia/europe/america",
                    "session_characteristics": "high_volume/low_volume/volatile/stable",
                    "funding_time_proximity": "immediate/near/far",
                    "optimal_entry_window": "now/1h/2h/4h/wait"
                }},
                "step7_position_strategy": {{
                    "entry_approach": "single_entry/split_3/split_5/dca_ladder",
                    "position_size_distribution": {{
                        "first_entry": 0.3-0.6,
                        "second_entry": 0.2-0.4,
                        "third_entry": 0.1-0.3
                    }},
                    "stop_loss_strategy": "tight_scalp/swing_wide/trailing",
                    "take_profit_approach": "partial_scaling/full_exit/hold_runner"
                }},
                "step8_adaptation_triggers": {{
                    "leverage_increase_conditions": ["condition1", "condition2"],
                    "leverage_decrease_conditions": ["condition1", "condition2"],
                    "position_size_increase": ["trigger1", "trigger2"],
                    "position_size_decrease": ["trigger1", "trigger2"],
                    "strategy_pivot_signals": ["signal1", "signal2"]
                }}
            }},
            "market_sentiment": "aggressive_bullish/moderate_bullish/neutral/moderate_bearish/aggressive_bearish",
            "confidence": 0-100,
            "profit_probability_4h": 0-100,
            "expected_move_4h": "percentage expected price movement in next 4 hours",
            "position_sizing_strategy": "single_large/split_3_entries/split_5_entries/dca_approach",
            "liquidation_risk": "low/medium/high/extreme",
            "margin_utilization": 0-100,
            "dynamic_leverage": {{
                "current_optimal": 5-20,
                "max_allowed": 5-20,
                "adjustment_reason": "volatility/trend/news/risk",
                "next_review": "15min/30min/1h/2h"
            }},
            "action_recommendation": "aggressive_long/moderate_long/scalp_long/hold/scalp_short/moderate_short/aggressive_short",
            "reasoning": "detailed step-by-step analysis summary focusing on profit opportunity and risk management",
            "entry_levels": {{
                "primary": price,
                "secondary": price,
                "tertiary": price
            }},
            "stop_loss": price,
            "take_profit_targets": [price1, price2, price3],
            "session_timing": "optimal/suboptimal/avoid",
            "funding_impact": "positive/neutral/negative",
            "volatility_score": 0-100,
            "market_regime": "trending_up/trending_down/ranging/volatile_up/volatile_down",
            "real_time_modifications": {{
                "leverage_adjustment_plan": "increase_on_volatility/decrease_on_volatility/maintain",
                "position_scaling_plan": "add_on_profit/reduce_on_loss/pyramid_up",
                "exit_modification": "tighten_stops/widen_stops/trail_profits"
            }}
        }}
        """
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            analysis = json.loads(response.content[0].text)
            return analysis
            
        except Exception as e:
            print(f"Claude 분석 오류: {e}")
            return {"error": str(e)}
    
    def analyze_social_sentiment(self, social_data: list) -> dict:
        """
        소셜 미디어 감정 분석 (Twitter, Reddit, 텔레그램)
        """
        prompt = f"""
        다음 소셜 미디어 데이터를 분석하여 암호화폐 시장 감정을 파악해주세요:
        
        {json.dumps(social_data, indent=2)}
        
        분석 요청사항:
        1. 전체적인 감정 점수 (-100 ~ +100)
        2. 주요 테마 및 키워드
        3. 영향력 있는 계정들의 논조
        4. 공포/탐욕 지수
        5. 밈/트렌드 영향도
        
        JSON으로 응답:
        {{
            "sentiment_score": -100 to 100,
            "dominant_emotion": "fear/greed/fomo/panic/euphoria",
            "key_themes": ["theme1", "theme2"],
            "influence_level": "low/medium/high",
            "crowd_behavior": "contrarian_signal/follow_crowd",
            "viral_content": ["content1", "content2"]
        }}
        """
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return json.loads(response.content[0].text)
            
        except Exception as e:
            return {"error": str(e)}
    
    def predict_volatility_events(self, historical_data: list, upcoming_events: list) -> dict:
        """
        Claude의 패턴 인식을 활용한 변동성 예측
        """
        prompt = f"""
        VOLATILITY PREDICTION for 24-hour futures trading system targeting 0.5% daily profit.
        
        Historical Data:
        {json.dumps(historical_data[-100:], indent=2)}
        
        Upcoming Events:
        {json.dumps(upcoming_events, indent=2)}
        
        Predict volatility with focus on PROFIT OPPORTUNITIES:
        
        1. Next 1-4 hours: Quick scalp opportunities (0.1-0.3% moves)
        2. Next 4-12 hours: Swing opportunities (0.3-0.8% moves) 
        3. Next 12-24 hours: Position trading opportunities (0.5-1.5% moves)
        4. FUNDING TIMES impact (00:00, 08:00, 16:00 UTC)
        5. SESSION TRANSITIONS (Asia->Europe->US volatility patterns)
        6. NEWS/EVENT driven volatility windows
        
        JSON Response:
        {{
            "volatility_probability_1h": 0-100,
            "volatility_probability_4h": 0-100,
            "volatility_probability_12h": 0-100,
            "expected_range_1h": {{"min": price, "max": price}},
            "expected_range_4h": {{"min": price, "max": price}},
            "expected_range_12h": {{"min": price, "max": price}},
            "optimal_trading_windows": ["1h-3h UTC", "8h-10h UTC", "15h-17h UTC"],
            "avoid_trading_windows": ["funding_times", "low_volume_periods"],
            "triggers": ["trigger1", "trigger2"],
            "profit_strategy": {{
                "scalp_opportunities": "1h windows with 0.1-0.3% moves",
                "swing_opportunities": "4h windows with 0.3-0.8% moves",
                "position_opportunities": "12h+ windows with 0.5%+ moves"
            }},
            "risk_events": ["high_impact_news", "funding_rate_changes"],
            "session_volatility": {{
                "asia": "low/medium/high",
                "europe": "low/medium/high", 
                "us": "low/medium/high"
            }},
            "funding_strategy": "increase_before/reduce_before/ignore",
            "preparation_strategy": "aggressive_long/moderate_long/reduce_exposure/aggressive_short/moderate_short"
        }}
        """
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return json.loads(response.content[0].text)
            
        except Exception as e:
            return {"error": str(e)}
    
    def generate_narrative_analysis(self, market_data: dict) -> str:
        """
        시장 상황을 스토리텔링으로 설명
        """
        prompt = f"""
        현재 시장 상황을 마치 경험 많은 트레이더가 후배에게 설명하듯 서술해주세요:
        
        시장 데이터:
        {json.dumps(market_data, indent=2)}
        
        다음 요소들을 포함해서 설명해주세요:
        1. 현재 무엇이 일어나고 있는가?
        2. 왜 이런 움직임이 나타나는가?
        3. 다른 트레이더들은 어떻게 생각하고 있을까?
        4. 다음에 일어날 가능성이 높은 시나리오는?
        5. 어떤 함정이나 위험이 숨어있을까?
        
        전문적이지만 이해하기 쉽게 설명해주세요.
        """
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"분석 생성 오류: {e}"

class MarketDataCollector:
    """
    Claude 분석을 위한 다양한 데이터 수집
    """
    
    def __init__(self):
        self.data_sources = {
            'news': 'https://api.newsapi.org/v2/everything',
            'social': 'https://api.twitter.com/2/tweets/search',
            'fear_greed': 'https://api.alternative.me/fng/',
            'economic': 'https://api.economicalendar.com/events'
        }
    
    def collect_news_data(self, symbol: str, hours: int = 24) -> list:
        """
        최근 뉴스 수집
        """
        # 실제 구현에서는 News API 사용
        mock_news = [
            {
                "title": "비트코인 ETF 승인 임박",
                "content": "SEC가 비트코인 현물 ETF 승인을 검토 중",
                "sentiment": "positive",
                "source": "블룸버그",
                "timestamp": datetime.now().isoformat()
            },
            {
                "title": "연준 금리 인상 신호",
                "content": "연준이 추가 금리 인상 가능성을 시사",
                "sentiment": "negative",
                "source": "로이터",
                "timestamp": datetime.now().isoformat()
            }
        ]
        return mock_news
    
    def collect_social_data(self, symbol: str) -> list:
        """
        소셜 미디어 데이터 수집
        """
        # 실제 구현에서는 Twitter API, Reddit API 사용
        mock_social = [
            {
                "platform": "twitter",
                "content": "#Bitcoin is going to the moon! 🚀",
                "author": "@crypto_whale",
                "engagement": 1500,
                "sentiment": "bullish"
            },
            {
                "platform": "reddit",
                "content": "시장이 너무 과열된 것 같다. 조정 올 듯",
                "subreddit": "r/cryptocurrency",
                "upvotes": 230,
                "sentiment": "bearish"
            }
        ]
        return mock_social
    
    def collect_economic_calendar(self) -> list:
        """
        경제 지표 일정 수집
        """
        mock_events = [
            {
                "event": "미국 CPI 발표",
                "date": (datetime.now() + timedelta(hours=12)).isoformat(),
                "importance": "high",
                "expected_impact": "high_volatility"
            },
            {
                "event": "FOMC 회의록 공개",
                "date": (datetime.now() + timedelta(days=2)).isoformat(),
                "importance": "medium",
                "expected_impact": "medium_volatility"
            }
        ]
        return mock_events
