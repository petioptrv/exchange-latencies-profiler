import json
from typing import Any, Tuple

from src.clients.ws_clients.ws_client_base import WSClientBase


class BinanceWSClient(WSClientBase):
    @property
    def url(self) -> str:
        return f"wss://stream.binance.com:9443/ws/{self._symbol.lower()}@trade"

    def on_open(self, ws):
        pass

    def _process_message(self, message: Any) -> Tuple[str, float, float]:
        data = json.loads(message)
        trade_id = str(data["t"])
        event_ts = data["E"] * 1e-3
        volume_in_quote = float(data["q"]) * float(data["p"])
        return trade_id, event_ts, volume_in_quote
