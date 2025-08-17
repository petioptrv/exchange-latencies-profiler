import time


def get_utc_ts() -> float:
    return time.time()


def sleep_for(seconds: float):
    time.sleep(seconds)
