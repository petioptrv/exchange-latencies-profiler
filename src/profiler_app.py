from sqlmodel import Session

from src.clients.rest_clients.binance_rest_client import BinanceRESTClient
from src.clients.ws_clients.binance_ws_client import BinanceWSClient
from src.config import settings
from src.data import ProfilerInstanceSpec
from src.db.crud import get_cloud_instance, get_exchange_instance
from src.db.db import engine
from src.db.db_cleaner import DBCleaner, DBCleanerPassthrough
from src.logging_utils import setup_logging
from src.profiler import Profiler


def main():
    setup_logging()

    with Session(engine) as session:
        cloud_instance = get_cloud_instance(
            session=session,
            provider=settings.CLOUD_PROVIDER,
            region_id=settings.CLOUD_REGION_ID,
            location=settings.CLOUD_LOCATION,
            longitude=settings.CLOUD_LOCATION_LONGITUDE,
            latitude=settings.CLOUD_LOCATION_LATITUDE,
            create_if_not_exist=True,
        )
        cloud_instance_id = cloud_instance.id
        exchange_instance = get_exchange_instance(
            session=session,
            name=settings.EXCHANGE_NAME,
            server_location=settings.EXCHANGE_SERVER_LOCATION,
            create_if_not_exist=True,
        )
        exchange_instance_id = exchange_instance.id
    instance_spec = ProfilerInstanceSpec(
        symbol=settings.SYMBOL,
        cloud_instance_id=cloud_instance_id,
        exchange_id=exchange_instance_id,
    )
    if settings.RUN_DB_CLEANER:
        db_cleaner = DBCleaner(instance_spec=instance_spec)
    else:
        db_cleaner = DBCleanerPassthrough(instance_spec=instance_spec)
    profiler = Profiler(
        instance_spec=instance_spec,
        rest_client=BinanceRESTClient(),
        threaded_trades_streamer_class=BinanceWSClient,
        trades_streamers_count=settings.STREAMERS_COUNT,
        db_cleaner=db_cleaner,
    )

    profiler.run()


if __name__ == "__main__":
    main()
