import logging
from collections import deque
from threading import Thread, Event
from typing import Deque, Optional, Dict

import numpy

from src.constants import CLOCK_SYNC_SAMPLES
from src.clients.rest_clients.rest_client_base import RESTClientBase
from src.time.server_time_provider import ServerTimeProvider
from src.time.utils import sleep_for

logger = logging.getLogger(__name__)


class TimeSynchronizer(Thread):
    def __init__(
        self,
        rest_client: RESTClientBase,
        server_time_provider: ServerTimeProvider,
        thread_kwargs: Optional[Dict] = None,
    ):
        super().__init__(**(thread_kwargs or {}))
        self._rest_client = rest_client
        self._server_time_provider = server_time_provider
        self._time_offset_ms_queue: Deque[float] = deque(maxlen=CLOCK_SYNC_SAMPLES)
        self._time_offset_ms = -1
        self._stopped = False

    @property
    def ready(self) -> bool:
        return len(self._time_offset_ms_queue) == self._time_offset_ms_queue.maxlen

    def run(self):
        logger.info("Starting the time synchronizer.")
        self._stopped = False
        last_update_minute = 0
        while not self._stopped:
            self._update_server_time()
            sleep_for(2)
            current_minute = self._server_time_provider.local_clock_ts // 60
            if current_minute > last_update_minute:
                logger.info(
                    f"local time = {self._server_time_provider.local_clock_ts}::"
                    f" server time = {self._server_time_provider.server_time}"
                )
                last_update_minute = current_minute
        logger.info("Stopping the time synchronizer.")

    def stop(self):
        self._stopped = True

    def _update_server_time(self):
        logger.debug("Updating server time...")
        local_before_ms: float = self._server_time_provider.local_clock_ts * 1e3
        server_time_ms: float = self._rest_client.get_server_time_ms()
        local_after_ms: float = self._server_time_provider.local_clock_ts * 1e3
        local_server_time_pre_image_ms: float = (local_before_ms + local_after_ms) / 2.0
        time_offset_ms: float = server_time_ms - local_server_time_pre_image_ms
        self._time_offset_ms_queue.append(time_offset_ms)
        self._compute_time_offset_ms()

    def _compute_time_offset_ms(self):
        median = numpy.median(self._time_offset_ms_queue)
        weighted_average = numpy.average(
            self._time_offset_ms_queue, weights=range(1, len(self._time_offset_ms_queue) * 2 + 1, 2)
        )
        self._time_offset_ms = numpy.mean([median, weighted_average])
