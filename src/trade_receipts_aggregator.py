import logging
import sys
from collections import defaultdict
from typing import List

from eventkit import Event
from pydantic import BaseModel

from src.data import TradeReceipt
from src.time.utils import get_utc_ts

logger = logging.getLogger(__name__)


class TradeReceiptsAggregator:
    def __init__(self, n_clients: int):
        self.aggregation_event: Event = Event()

        self._n_clients = n_clients
        self._in_flight_trade_aggregations: dict[str, TradeAggregation] = defaultdict(
            lambda: TradeAggregation(expected_trade_receipts=self._n_clients, started_ts=get_utc_ts())
        )
        self._current_minute_trade_latencies: List[float] = []
        self._current_minute_volume_in_quote: float = 0
        self._last_aggregation_minute = self._get_current_minute_since_epoch()

    def add_trade_receipt(self, trade_receipt: TradeReceipt):
        trade_aggregation = self._in_flight_trade_aggregations[trade_receipt.id]
        trade_aggregation.log_trade_receipt(trade_receipt=trade_receipt)
        if trade_aggregation.done:
            self._process_and_pop_trade_aggregation(trade_id=trade_receipt.id)
        aggregation_minute = self._get_current_minute_since_epoch()
        if aggregation_minute > self._last_aggregation_minute:
            self._issue_aggregation()
            self._reset_aggregation()
            self._clean_pending_trades()
            self._last_aggregation_minute = aggregation_minute

    def _process_and_pop_trade_aggregation(self, trade_id: str):
        trade_aggregation = self._in_flight_trade_aggregations.pop(trade_id)
        self._current_minute_trade_latencies.append(trade_aggregation.min_latency)
        self._current_minute_volume_in_quote += trade_aggregation.volume_in_quote

    def _issue_aggregation(self):
        if len(self._current_minute_trade_latencies) != 0:
            aggregation_ts = (self._get_current_minute_since_epoch() - 1) * 60
            aggregation = MinuteTradesAggregation(
                timestamp=aggregation_ts,
                average_trade_latency=sum(self._current_minute_trade_latencies) / len(self._current_minute_trade_latencies),
                min_trade_latency=min(self._current_minute_trade_latencies),
                max_trade_latency=max(self._current_minute_trade_latencies),
                total_trade_volume_in_quote=self._current_minute_volume_in_quote,
            )
            self.aggregation_event.emit(aggregation)

    def _reset_aggregation(self):
        self._current_minute_trade_latencies.clear()
        self._current_minute_volume_in_quote: float = 0

    def _clean_pending_trades(self):
        current_ts = get_utc_ts()
        for trade_id, pending_trade in list(self._in_flight_trade_aggregations.items()):
            if pending_trade.started_ts < current_ts - 60:
                logger.warning(f"Trade {trade_id} never received confirmation from all clients.")
                self._in_flight_trade_aggregations.pop(trade_id)

    def _get_current_minute_since_epoch(self) -> int:
        ts = get_utc_ts()
        return self._get_minute_from_timestamp(timestamp=ts)

    @staticmethod
    def _get_minute_from_timestamp(timestamp: float) -> int:
        return int(timestamp // 60)


class TradeAggregation(BaseModel):
    started_ts: float
    expected_trade_receipts: int
    logged_trade_receipts: int = 0
    min_latency: float = sys.maxsize
    volume_in_quote: float = 0

    @property
    def done(self) -> bool:
        return self.logged_trade_receipts == self.expected_trade_receipts

    def log_trade_receipt(self, trade_receipt: TradeReceipt):
        self.logged_trade_receipts += 1
        self.volume_in_quote = trade_receipt.volume_in_quote
        if self.logged_trade_receipts > self.expected_trade_receipts:
            raise RuntimeError("Received more trade confirmations that there are clients.")
        self.min_latency = min(self.min_latency, trade_receipt.latency)


class MinuteTradesAggregation(BaseModel):
    timestamp: float
    average_trade_latency: float
    min_trade_latency: float
    max_trade_latency: float
    total_trade_volume_in_quote: float
