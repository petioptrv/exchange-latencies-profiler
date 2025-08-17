import logging
from abc import ABC, abstractmethod
from queue import Queue
from typing import Any, Tuple, Optional, Dict

import websocket

from src.clients.threaded_streamer_base import ThreadedTradesStreamerBase
from src.time.server_time_provider import ServerTimeProvider
from src.time.utils import sleep_for

logger = logging.getLogger(__name__)


class WSClientBase(ThreadedTradesStreamerBase, ABC):
    def __init__(
        self,
        symbol: str,
        out_queue: Queue,
        server_time_provider: ServerTimeProvider,
        streamer_kwargs: Optional[Dict] = None,
        thread_kwargs: Optional[Dict] = None,
    ):
        super().__init__(
            symbol=symbol,
            out_queue=out_queue,
            server_time_provider=server_time_provider,
            streamer_kwargs=streamer_kwargs,
            thread_kwargs=thread_kwargs,
        )
        self._ws: Optional[websocket.WebSocketApp] = None
        self._stopped = False

    @property
    @abstractmethod
    def url(self) -> str:
        ...

    @abstractmethod
    def on_open(self, ws):
        ...

    @abstractmethod
    def _process_message(self, message: Any) -> Tuple[str, float, float]:
        ...

    def on_message(self, ws, msg):
        trade_id, event_ts, volume = self._process_message(message=msg)
        self.stream_receipt(trade_id=trade_id, event_ts=event_ts, volume=volume)

    def on_error(self, ws, err):
        logger.error(err)

    def run(self):
        self._stopped = False
        self._ws = websocket.WebSocketApp(
            self.url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
        )

        while not self._stopped:
            try:
                self._ws.run_forever(ping_interval=20, ping_timeout=10)
            except KeyboardInterrupt:
                logger.info("Closing websocket connection")
            except Exception:
                logger.exception("Error in WS listener.")
                sleep_for(seconds=1)

        try:
            self._ws.close()
        except Exception:
            pass

    def stop(self):
        self._stopped = True
        if self._ws is not None:
            self._ws.close()
