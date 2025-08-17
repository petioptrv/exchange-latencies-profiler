from threading import Thread, Event
from typing import Dict, Optional
from datetime import datetime, timedelta, time, timezone
import logging
from sqlmodel import Session

from src.data import ProfilerInstanceSpec
from src.db.crud import delete_old_historical_minute_trade_latencies


class DBCleaner(Thread):
    def __init__(
        self,
        instance_spec: ProfilerInstanceSpec,
        thread_kwargs: Optional[Dict] = None,
    ):
        super().__init__(**(thread_kwargs or {}))
        self._instance_spec = instance_spec
        self._stop_event = Event()
        self._logger = logging.getLogger(__name__)

    def run(self):
        self._logger.info("DB Cleaner thread started")

        while not self._stop_event.is_set():
            now = datetime.now(timezone.utc)
            midnight = datetime.combine(now.date() + timedelta(days=1), time.min)
            seconds_until_midnight = (midnight - now).total_seconds()

            if not self._stop_event.wait(timeout=seconds_until_midnight):
                try:
                    self._clean_historical_data()
                except Exception as e:
                    self._logger.error(f"Error during database cleanup: {e}")

    def _clean_historical_data(self):
        engine = self._instance_spec.engine
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=8)  # One week + one day

        with Session(engine) as session:
            delete_old_historical_minute_trade_latencies(session=session, cutoff_date=cutoff_date)

        self._logger.info(f"Deleted historical entries older than {cutoff_date}")

    def stop(self):
        self._logger.info("Stopping DB Cleaner thread")
        self._stop_event.set()
