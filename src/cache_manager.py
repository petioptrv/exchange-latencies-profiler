import threading
import time
from typing import List

from src.api.responses import DataResponse


class DataCache:
    def __init__(self):
        self._data: List[DataResponse] = []
        self._last_updated: float = 0.0
        self._lock = threading.Lock()

    def set(self, data: List[DataResponse]) -> None:
        with self._lock:
            self._data = data
            self._last_updated = time.time()

    def get(self) -> List[DataResponse]:
        with self._lock:
            return self._data

    def age_seconds(self) -> float:
        with self._lock:
            return time.time() - self._last_updated if self._last_updated else float("inf")


cache = DataCache()
