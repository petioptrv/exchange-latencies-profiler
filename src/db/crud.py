from datetime import datetime

from sqlalchemy import delete
from sqlmodel import Session, select
from src.db.model import CloudInstance, Exchange, HistoricalMinuteTradeLatenciesEntry


def get_cloud_instance(
    *,
    session: Session,
    provider: str,
    region_id: str,
    location: str,
    create_if_not_exist: bool = False,
) -> CloudInstance:
    statement = select(CloudInstance).where(
        CloudInstance.provider == provider,
        CloudInstance.region_id == region_id,
        CloudInstance.location == location,
    )
    instance = session.exec(statement).first()

    if instance is None:
        if create_if_not_exist:
            instance = CloudInstance(
                provider=provider,
                region_id=region_id,
                location=location,
            )
            session.add(instance)
            session.commit()
            session.refresh(instance)
        else:
            raise ValueError(
                f"Cloud instance not found for provider={provider}, "
                f"region_id={region_id}, location={location}"
            )

    return instance


def get_exchange_instance(
    *,
    session: Session,
    name: str,
    server_location: str,
    create_if_not_exist: bool = False,
) -> Exchange:
    statement = select(Exchange).where(
        Exchange.name == name,
        Exchange.server_location == server_location,
    )
    instance = session.exec(statement).first()

    if instance is None:
        if create_if_not_exist:
            instance = Exchange(
                name=name,
                server_location=server_location,
            )
            session.add(instance)
            session.commit()
            session.refresh(instance)
        else:
            raise ValueError(
                f"Exchange instance not found for name={name}, "
                f"server_location={server_location}"
            )

    return instance


def delete_old_historical_minute_trade_latencies(
    *,
    session: Session,
    cutoff_date: datetime,
):
    delete_stmt = delete(HistoricalMinuteTradeLatenciesEntry).where(
        HistoricalMinuteTradeLatenciesEntry.timestamp < cutoff_date
    )
    session.exec(delete_stmt)
    session.commit()
