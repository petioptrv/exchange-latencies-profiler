from abc import ABC, abstractmethod
from queue import Queue
from threading import Thread
from typing import Optional, Dict

from src.data import TradeReceipt
from src.time.server_time_provider import ServerTimeProvider


class ThreadedTradesStreamerBase(Thread, ABC):
    def __init__(
        self,
        symbol: str,
        out_queue: Queue,
        server_time_provider: ServerTimeProvider,
        streamer_kwargs: Optional[Dict] = None,
        thread_kwargs: Optional[Dict] = None,
    ):
        super().__init__(**(thread_kwargs or {}))
        self._symbol = symbol
        self._out_queue = out_queue
        self._server_time_provider = server_time_provider

    @abstractmethod
    def run(self):
        ...

    @abstractmethod
    def stop(self):
        ...

    def stream_receipt(self, trade_id: str, event_ts: float, volume: float):
        receipt = TradeReceipt(
            id=trade_id,
            timestamp=event_ts,
            latency=self._server_time_provider.server_time - event_ts,
            volume=volume,
        )
        self._out_queue.put_nowait(item=receipt)
