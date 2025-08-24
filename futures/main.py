# futures/main.py - 선물 거래 올인원
import asyncio
from time_manager import TimeBasedManager
from session_monitor import SessionMonitor
from backtester import FuturesBacktester


async def main():
    print("🚀 BTC 선물 시간대 최적화 트레이더")
    print("1. 🧪 백테스트")
    print("2. 📊 실시간 모니터")
    print("3. 🔥 실거래")
    choice = input("선택: ")

    if choice == "1":
        backtester = FuturesBacktester()
        await backtester.run()
    elif choice == "2":
        monitor = SessionMonitor()
        await monitor.run()
    else:
        trader = TimeBasedManager()
        await trader.start()


if __name__ == "__main__":
    asyncio.run(main())
