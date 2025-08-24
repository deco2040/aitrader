import datetime

class FuturesTimeManager:
    def __init__(self):
        pass

    def get_current_time(self):
        return datetime.datetime.now()

    def get_specific_time(self, year, month, day, hour, minute, second):
        return datetime.datetime(year, month, day, hour, minute, second)

    def get_time_difference(self, time1, time2):
        return abs((time1 - time2).total_seconds())