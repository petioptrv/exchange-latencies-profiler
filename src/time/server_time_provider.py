import time


class ServerTimeProvider:
    def __init__(self):
        self._server_time_offset_ms = -1

    @property
    def server_time(self) -> float:
        return self.local_clock_ts + self._server_time_offset_ms * 1e-3

    @property
    def local_clock_ts(self):
        return time.time()

    def set_server_time_offset_ms(self, server_time_offset_ms: int):
        self._server_time_offset_ms = server_time_offset_ms
