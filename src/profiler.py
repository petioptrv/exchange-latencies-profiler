import logging
import queue
from datetime import datetime, timezone
from typing import Type, Dict, Optional, List

from sqlmodel import Session

from src.clients.rest_clients.rest_client_base import RESTClientBase
from src.clients.threaded_streamer_base import ThreadedTradesStreamerBase
from src.data import ProfilerInstanceSpec
from src.db.db import engine
from src.db.db_cleaner import DBCleaner
from src.db.model import HistoricalMinuteTradeLatenciesEntry
from src.time.server_time_provider import ServerTimeProvider
from src.time.time_synchronizer import TimeSynchronizer
from src.time.utils import sleep_for
from src.trade_receipts_aggregator import TradeReceiptsAggregator, MinuteTradesAggregation

logger = logging.getLogger(__name__)


class Profiler:
    def __init__(
        self,
        instance_spec: ProfilerInstanceSpec,
        rest_client: RESTClientBase,
        threaded_trades_streamer_class: Type[ThreadedTradesStreamerBase],
        trades_streamers_count: int,
        db_cleaner: DBCleaner,
        streamer_kwargs: Optional[Dict] = None,
        streamer_threads_kwargs: Optional[Dict] = None,
    ):

        self._instance_spec = instance_spec
        self._server_time_provider = ServerTimeProvider()
        self._time_synchronizer = TimeSynchronizer(
            rest_client=rest_client, server_time_provider=self._server_time_provider
        )
        self._trade_receipts_aggregator = TradeReceiptsAggregator(n_clients=trades_streamers_count)
        self._trade_receipts_aggregator.aggregation_event += self._on_trade_receipt_aggregation_event
        self._out_queue = queue.Queue()
        self._threaded_trades_streamers = [
            threaded_trades_streamer_class(
                symbol=self._instance_spec.symbol,
                out_queue=self._out_queue,
                server_time_provider=self._server_time_provider,
                streamer_kwargs=streamer_kwargs,
                thread_kwargs=streamer_threads_kwargs,
            ) for _ in range(trades_streamers_count)
        ]
        self._db_cleaner = db_cleaner

        self._aggregation_events: List[MinuteTradesAggregation] = []
        self._last_db_update_minute = 0

    def run(self):
        self._time_synchronizer.start()

        while not self._time_synchronizer.ready:
            logger.info("Awaiting time synchronizer initialization...")
            sleep_for(seconds=5)

        for streamer in self._threaded_trades_streamers:
            streamer.start()
        self._db_cleaner.start()

        try:
            while True:
                trade_receipt = self._out_queue.get()
                self._trade_receipts_aggregator.add_trade_receipt(trade_receipt=trade_receipt)

        except KeyboardInterrupt:
            for streamer in self._threaded_trades_streamers:
                streamer.stop()
            self._time_synchronizer.stop()
            self._db_cleaner.stop()

            for streamer in self._threaded_trades_streamers:
                streamer.join()
            self._time_synchronizer.join()
            self._db_cleaner.join()

    def _on_trade_receipt_aggregation_event(self, event: MinuteTradesAggregation):
        self._aggregation_events.append(event)
        current_minute = self._server_time_provider.local_clock_ts // 60
        if current_minute > self._last_db_update_minute:
            self._issue_db_update()
            self._last_db_update_minute = current_minute

    def _issue_db_update(self):
        logger.info(f"Updating db with {len(self._aggregation_events)} aggregation(s).")
        with Session(engine) as session:
            for event in self._aggregation_events:
                update = HistoricalMinuteTradeLatenciesEntry(
                    session=session,
                    cloud_instance_id=self._instance_spec.cloud_instance_id,
                    exchange_id=self._instance_spec.exchange_id,
                    timestamp=datetime.fromtimestamp(event.timestamp, tz=timezone.utc),
                    average_trade_latency=event.average_trade_latency,
                    min_trade_latency=event.min_trade_latency,
                    max_trade_latency=event.max_trade_latency,
                    total_trade_volume=event.total_trade_volume,
                )
                session.add(update)
            session.commit()
        self._aggregation_events.clear()
