from sqlmodel import Session

from src.clients.rest_clients.binance_rest_client import BinanceRESTClient
from src.clients.ws_clients.binance_ws_client import BinanceWSClient
from src.config import settings
from src.data import ProfilerInstanceSpec
from src.db.crud import get_cloud_instance, get_exchange_instance
from src.db.db import engine
from src.logging_config import setup_logging
from src.profiler import Profiler


def main():
    setup_logging()

    with Session(engine) as session:
        cloud_instance = get_cloud_instance(
            session=session,
            provider=settings.CLOUD_PROVIDER,
            region_id=settings.CLOUD_REGION_ID,
            location=settings.CLOUD_LOCATION,
            create_if_not_exist=True,
        )
        exchange_instance = get_exchange_instance(
            session=session,
            name=settings.EXCHANGE_NAME,
            server_location=settings.EXCHANGE_SERVER_LOCATION,
            create_if_not_exist=True,
        )
    instance_spec = ProfilerInstanceSpec(
        symbol=settings.SYMBOL,
        cloud_instance=cloud_instance,
        exchange=exchange_instance,
    )
    profiler = Profiler(
        instance_spec=instance_spec,
        rest_client=BinanceRESTClient(),
        threaded_trades_streamer_class=BinanceWSClient,
        trades_streamers_count=settings.STREAMERS_COUNT,
    )

    profiler.run()


if __name__ == "__main__":
    main()
