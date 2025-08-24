
# futures/main.py - 선물 마진 거래 올인원
import asyncio
import logging
from datetime import datetime
from claude_client import FuturesClaudeClient
from mcp_client import FuturesMCPClient
from config import *

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class FuturesTrader:

    def __init__(self):
        self.claude = FuturesClaudeClient()
        self.mcp = FuturesMCPClient()
        self.running = False
        
        # 상태 추적
        self.current_position = 0.0  # BTC 포지션
        self.entry_price = 0.0
        self.current_leverage = 0
        self.daily_pnl = 0.0
        self.trade_count = 0
        self.total_fees_paid = 0.0
        self.liquidation_warnings = 0

    async def start_futures_trading(self):
        """선물 거래 시작"""
        print("🚀 BTC 선물 마진거래 시스템 시작")
        print(f"⚡ 레버리지: {LEVERAGE}배")
        print(f"🎯 일일목표: {DAILY_TARGET*100:.1f}%")
        print(f"⚠️ 최대손실: {MAX_DAILY_LOSS*100:.1f}%")
        print(f"💰 포지션크기: ${POSITION_SIZE}")

        # 초기 설정
        try:
            await self._initialize_futures_account()
            self.running = True
            
            # 메인 루프들 시작
            await asyncio.gather(
                self.trading_loop(),
                self.risk_management_loop(),
                self.funding_monitor_loop()
            )
            
        except Exception as e:
            logging.error(f"❌ 시스템 오류: {e}")
            await self.emergency_stop()

    async def _initialize_futures_account(self):
        """선물 계정 초기화"""
        # 레버리지 설정
        await self.mcp.set_leverage(SYMBOL, LEVERAGE)
        logging.info(f"⚡ 레버리지 {LEVERAGE}배 설정 완료")
        
        # 마진 모드 설정 (isolated 권장)
        await self.mcp.set_margin_mode(SYMBOL, "isolated")
        logging.info("🛡️ 격리 마진 모드 설정 완료")
        
        # 미체결 주문 정리
        await self.mcp.cancel_all_orders(SYMBOL)
        logging.info("🧹 미체결 주문 정리 완료")

    async def trading_loop(self):
        """메인 거래 루프"""
        while self.running:
            try:
                # 거래 한도 체크
                if self.trade_count >= MAX_DAILY_TRADES:
                    await asyncio.sleep(ANALYSIS_INTERVAL)
                    continue

                # 시장 데이터 수집
                ticker = await self.mcp.fetch_ticker(SYMBOL)
                positions = await self.mcp.fetch_positions(SYMBOL)
                account = await self.mcp.get_account_info()
                funding = await self.mcp.fetch_funding_rate(SYMBOL)

                if not ticker:
                    await asyncio.sleep(30)
                    continue

                current_price = ticker['last']
                change_24h = ticker.get('percentage', 0)

                # 현재 포지션 정보
                position_info = await self.mcp.get_position_info(SYMBOL)
                self.current_position = position_info.get('size', 0)
                
                # 시장 데이터 구성
                market_data = {
                    "price": current_price,
                    "change_24h": change_24h,
                    "position_size": self.current_position,
                    "unrealized_pnl": position_info.get('unrealized_pnl_percentage', 0),
                    "margin_ratio": position_info.get('margin_ratio', 1.0),
                    "liquidation_price": position_info.get('liquidation_price', 0),
                    "current_leverage": self.current_leverage,
                    "funding_rate": funding.get('rate', 0) if funding else 0,
                    "daily_pnl": self.daily_pnl,
                    "trade_count": self.trade_count
                }

                # AI 분석
                decision = await self.claude.futures_analyze(market_data)
                await self._execute_futures_decision(decision, current_price)

                # 상태 로깅
                pos_info = f"{'L' if self.current_position > 0 else 'S' if self.current_position < 0 else 'N'}"
                logging.info(f"📊 ${current_price:,.0f} ({change_24h:+.1f}%) | "
                           f"{pos_info}:{abs(self.current_position):.4f} | "
                           f"PnL:{market_data['unrealized_pnl']:+.1f}% | {decision['action']}")

            except Exception as e:
                logging.error(f"❌ 거래루프 오류: {e}")

            await asyncio.sleep(ANALYSIS_INTERVAL)

    async def _execute_futures_decision(self, decision, current_price):
        """선물 거래 결정 실행"""
        action = decision['action']
        leverage = decision.get('leverage', LEVERAGE)
        
        try:
            if action == 'buy' and self.current_position <= 0:
                # 롱 포지션 진입
                await self._execute_long_entry(current_price, leverage)
                
            elif action == 'sell' and self.current_position >= 0:
                # 숏 포지션 진입
                await self._execute_short_entry(current_price, leverage)
                
            elif action == 'close' and self.current_position != 0:
                # 포지션 청산
                close_ratio = decision.get('close_ratio', 1.0)
                await self._execute_position_close(close_ratio)

        except Exception as e:
            logging.error(f"❌ 거래 실행 실패: {e}")

    async def _execute_long_entry(self, price, leverage):
        """롱 포지션 진입"""
        if self.current_position < 0:
            # 기존 숏 포지션 청산
            await self.mcp.close_position(SYMBOL)
            
        result = await self.mcp.long_market(SYMBOL, POSITION_SIZE, leverage)
        
        if result and result.get('status') == 'closed':
            self.entry_price = result.get('average', price)
            self.current_leverage = leverage
            self.trade_count += 1
            
            fee = result.get('fee', {}).get('cost', 0)
            self.total_fees_paid += fee
            
            logging.info(f"🟢 롱 진입: ${self.entry_price:,.0f} | {leverage}배 | 수수료: ${fee:.2f}")

    async def _execute_short_entry(self, price, leverage):
        """숏 포지션 진입"""
        if self.current_position > 0:
            # 기존 롱 포지션 청산
            await self.mcp.close_position(SYMBOL)
            
        result = await self.mcp.short_market(SYMBOL, POSITION_SIZE, leverage)
        
        if result and result.get('status') == 'closed':
            self.entry_price = result.get('average', price)
            self.current_leverage = leverage
            self.trade_count += 1
            
            fee = result.get('fee', {}).get('cost', 0)
            self.total_fees_paid += fee
            
            logging.info(f"🔴 숏 진입: ${self.entry_price:,.0f} | {leverage}배 | 수수료: ${fee:.2f}")

    async def _execute_position_close(self, close_ratio=1.0):
        """포지션 청산"""
        if self.current_position == 0:
            return
            
        close_amount = abs(self.current_position) * close_ratio
        
        # 부분 청산 또는 전체 청산
        if close_ratio >= 1.0:
            result = await self.mcp.close_position(SYMBOL)
        else:
            side = 'sell' if self.current_position > 0 else 'buy'
            result = await self.mcp.create_market_order(SYMBOL, side, close_amount)

        if result and result.get('status') == 'closed':
            fee = result.get('fee', {}).get('cost', 0)
            self.total_fees_paid += fee
            self.trade_count += 1
            
            # 수익 계산
            avg_close_price = result.get('average', 0)
            if self.current_position > 0:
                profit_per_btc = avg_close_price - self.entry_price
            else:
                profit_per_btc = self.entry_price - avg_close_price
                
            profit_usd = profit_per_btc * close_amount
            profit_pct = (profit_usd / POSITION_SIZE) * 100 * self.current_leverage
            
            self.daily_pnl += profit_pct
            
            emoji = "🟢" if profit_pct > 0 else "🔴"
            logging.info(f"{emoji} 청산({close_ratio*100:.0f}%): ${avg_close_price:,.0f} | "
                        f"수익: {profit_pct:+.2f}% | 수수료: ${fee:.2f}")
            
            # 포지션 업데이트
            if close_ratio >= 1.0:
                self.current_position = 0.0
                self.entry_price = 0.0
                self.current_leverage = 0

    async def risk_management_loop(self):
        """리스크 관리 루프"""
        while self.running:
            await asyncio.sleep(RISK_INTERVAL)
            
            try:
                # 일일 손실 한도 체크
                if abs(self.daily_pnl) >= MAX_DAILY_LOSS * 100:
                    logging.critical(f"🚨 일일 손실 한도 도달: {self.daily_pnl:.2f}%")
                    await self.emergency_stop()
                    break

                # 포지션이 있을 때 리스크 체크
                if self.current_position != 0:
                    position_info = await self.mcp.get_position_info(SYMBOL)
                    margin_ratio = position_info.get('margin_ratio', 1.0)
                    liquidation_price = position_info.get('liquidation_price', 0)
                    
                    # 청산 위험 경고
                    if margin_ratio < RISK_MANAGEMENT['liquidation_warning']:
                        self.liquidation_warnings += 1
                        logging.warning(f"⚠️ 청산 위험! 마진비율: {margin_ratio:.2f}")
                        
                        # 자동 청산 (50%)
                        if margin_ratio < RISK_MANAGEMENT['margin_ratio_min']:
                            logging.critical("🚨 긴급 부분청산 실행")
                            await self._execute_position_close(0.5)

            except Exception as e:
                logging.error(f"❌ 리스크관리 오류: {e}")

    async def funding_monitor_loop(self):
        """펀딩 모니터링 루프"""
        while self.running:
            await asyncio.sleep(300)  # 5분마다 체크
            
            try:
                if self.current_position == 0:
                    continue
                    
                current_hour = datetime.utcnow().hour
                
                # 펀딩 시간 30분 전 체크
                if any(abs(current_hour - ft) < 1 for ft in FEES['funding_times']):
                    funding = await self.mcp.fetch_funding_rate(SYMBOL)
                    
                    if funding:
                        rate = funding.get('rate', 0)
                        
                        # 불리한 펀딩인 경우 경고
                        if (self.current_position > 0 and rate > 0.0005) or \
                           (self.current_position < 0 and rate < -0.0005):
                            logging.warning(f"💰 불리한 펀딩 예정: {rate*10000:+.1f}bps")

            except Exception as e:
                logging.error(f"❌ 펀딩모니터 오류: {e}")

    async def emergency_stop(self):
        """긴급 중단"""
        self.running = False
        logging.critical("🚨 긴급 중단 실행")
        
        try:
            # 모든 포지션 청산
            if self.current_position != 0:
                await self.mcp.close_position(SYMBOL)
                logging.warning("🚨 긴급 포지션 청산 완료")
                
            # 모든 주문 취소
            await self.mcp.cancel_all_orders(SYMBOL)
            
            # 최종 통계
            stats = self.claude.get_performance_stats()
            logging.info(f"📊 최종 결과:")
            logging.info(f"   💰 일일 PnL: {self.daily_pnl:.2f}%")
            logging.info(f"   🔄 거래 횟수: {self.trade_count}회")
            logging.info(f"   💸 총 수수료: ${self.total_fees_paid:.2f}")
            logging.info(f"   ⚠️ 청산 경고: {self.liquidation_warnings}회")
            
        except Exception as e:
            logging.error(f"❌ 긴급중단 오류: {e}")


async def main():
    print("🚀 BTC 선물 마진 거래 시스템")
    print("1. 🔥 실거래 시작")
    print("2. 🧪 백테스트")
    print("3. 📊 시장 모니터")
    
    choice = input("선택 (1-3): ")
    
    if choice == "1":
        trader = FuturesTrader()
        await trader.start_futures_trading()
        
    elif choice == "2":
        from backtester import FuturesBacktester
        backtester = FuturesBacktester()
        
        days = int(input("백테스트 기간 (일): ") or "3")
        from backtester import generate_futures_data
        price_data = generate_futures_data(days)
        
        await backtester.run_futures_backtest(price_data, days)
        
    elif choice == "3":
        from session_monitor import SessionMonitor
        monitor = SessionMonitor()
        await monitor.run()
        
    else:
        print("❌ 잘못된 선택")


if __name__ == "__main__":
    asyncio.run(main())
