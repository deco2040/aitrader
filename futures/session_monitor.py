# futures/session_monitor.py - 간단한 세션 모니터
import asyncio
from datetime import datetime


class SessionMonitor:

    def __init__(self):
        self.volume_stats = {
            0: 0.8,
            1: 0.7,
            2: 0.6,
            3: 0.5,
            4: 0.6,
            5: 0.7,
            6: 0.8,
            7: 0.9,
            8: 1.2,
            9: 1.4,
            10: 1.3,
            11: 1.2,
            12: 1.1,
            13: 1.8,
            14: 2.2,
            15: 2.5,
            16: 2.0,
            17: 1.8,
            18: 1.6,
            19: 1.4,
            20: 1.2,
            21: 1.0,
            22: 0.9,
            23: 0.8
        }

    async def run(self):
        print("📊 글로벌 세션 모니터")

        while True:
            current_hour = datetime.utcnow().hour
            volume = self.volume_stats[current_hour]

            print(f"\n⏰ UTC {current_hour:02d}시 | 거래량: {volume:.1f}배")

            if 13 <= current_hour <= 16:
                print("🔥 런던-뉴욕 중복시간 - 최고 거래량!")
            elif volume >= 1.5:
                print("⚡ 높은 거래량 - 공격적 거래 권장")
            elif volume < 0.8:
                print("😴 저활성 - 보수적 거래 권장")

            await asyncio.sleep(300)  # 5분마다 업데이트
