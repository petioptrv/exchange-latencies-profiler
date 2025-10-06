import logging
import threading
from collections import defaultdict
from typing import List

import numpy as np
from sqlmodel import Session

from src.api.deps import get_db
from src.api.responses import DataResponse
from src.cache_manager import cache
from src.config import settings
from src.db.crud import get_all_historical_minute_trade_latencies
from src.db.model import HistoricalMinuteTradeLatenciesEntry

logger = logging.getLogger(__name__)


class BackgroundRefresher:
    def __init__(self):
        self._stop_event = threading.Event()
        self._data_cache = cache

    def stop(self):
        self._stop_event.set()

    def refresher_loop(self, refresh_interval_seconds: int = 60):
        logger.info("Starting refresher loop")
        while not self._stop_event.is_set():
            try:
                logger.info("Refreshing local data.")
                for session in get_db():
                    data = self._build_response_from_db(session)
                    if data:
                        self._data_cache.set(data)
                    break
                logger.info("Local data refreshed.")
            except Exception:
                logger.exception("Error while refreshing DB data cache.")
            finally:
                self._stop_event.wait(refresh_interval_seconds)

    @staticmethod
    def _build_response_from_db(session: Session) -> List[DataResponse]:
        minutes_buckets = 60
        entries: List[HistoricalMinuteTradeLatenciesEntry] = get_all_historical_minute_trade_latencies(session=session)
        if not entries:
            return []

        bucket_latencies = defaultdict(list)
        bucket_volumes = defaultdict(list)

        for entry in entries:
            ts = entry.timestamp
            bucket_start = ts.replace(minute=(ts.minute // minutes_buckets) * minutes_buckets, second=0, microsecond=0)

            bucket_latencies[bucket_start].append(entry.average_trade_latency)
            bucket_volumes[bucket_start].append(entry.total_trade_volume_in_quote)

        aggregated_latencies = []
        aggregated_volumes = []

        for bucket_start in sorted(bucket_latencies.keys()):
            avg_latency = sum(bucket_latencies[bucket_start]) / len(bucket_latencies[bucket_start])
            avg_volume = sum(bucket_volumes[bucket_start]) / len(bucket_volumes[bucket_start])
            ts_seconds = bucket_start.timestamp()

            aggregated_latencies.append((avg_latency * 1e3, ts_seconds))
            aggregated_volumes.append((avg_volume * 1e3, ts_seconds))

        lat_values = [l for l, _ in aggregated_latencies]
        vol_values = [v for v, _ in aggregated_volumes]

        if 1 < len(lat_values) == len(vol_values):
            corr_matrix = np.corrcoef(lat_values, vol_values)
            correlation_value = float(corr_matrix[0, 1])
        else:
            correlation_value = None

        latest_entry = entries[-1]
        response = [
            DataResponse(
                location=settings.CLOUD_LOCATION,
                coords=(settings.CLOUD_LOCATION_LATITUDE, settings.CLOUD_LOCATION_LONGITUDE),
                latestLatency=latest_entry.average_trade_latency * 1e3,
                latencies=aggregated_latencies,
                volume=aggregated_volumes,
                correlation=correlation_value,
            )
        ]
        return response
