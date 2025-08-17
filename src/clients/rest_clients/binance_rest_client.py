import requests

from src.clients.rest_clients.rest_client_base import RESTClientBase


class BinanceRESTClient(RESTClientBase):
    def get_server_time_ms(self) -> float:
        url = "https://api.binance.com/api/v3/time"
        response = requests.get(url)
        data = response.json()
        server_time_ms = data["serverTime"]
        return server_time_ms
