from sqlmodel import Session, select
from src.db.model import CloudInstances, Exchanges


def get_cloud_instance(
    *,
    session: Session,
    provider: str,
    region_id: str,
    location: str,
    create_if_not_exist: bool = False,
) -> CloudInstances:
    statement = select(CloudInstances).where(
        CloudInstances.provider == provider,
        CloudInstances.region_id == region_id,
        CloudInstances.location == location,
    )
    instance = session.exec(statement).first()

    if instance is None:
        if create_if_not_exist:
            instance = CloudInstances(
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
) -> Exchanges:
    statement = select(Exchanges).where(
        Exchanges.name == name,
        Exchanges.server_location == server_location,
    )
    instance = session.exec(statement).first()

    if instance is None:
        if create_if_not_exist:
            instance = Exchanges(
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
