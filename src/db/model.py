from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float
from sqlmodel import SQLModel, Field, String, Column


class CloudInstance(SQLModel, table=True):
    __tablename__ = "cloud_instances"

    id: Optional[int] = Field(default=None, primary_key=True)
    provider: str = Field(sa_column=Column(String(20), nullable=False))
    region_id: str = Field(sa_column=Column(String(20), nullable=False))
    location: str = Field(sa_column=Column(String(20), nullable=False))
    longitude: float = Field(sa_column=Column(Float, nullable=False))
    latitude: float = Field(sa_column=Column(Float, nullable=False))


class Exchange(SQLModel, table=True):
    __tablename__ = "exchanges"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(20), nullable=False))
    server_location: str = Field(sa_column=Column(String(20), nullable=False))


class HistoricalMinuteTradeLatenciesEntry(SQLModel, table=True):
    __tablename__ = "historical_minute_trade_latencies"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    cloud_instance_id: Optional[int] = Field(default=None, foreign_key="cloud_instances.id")
    exchange_id: Optional[int] = Field(default=None, foreign_key="exchanges.id")
    timestamp: datetime = Field(sa_column=Column(DateTime, nullable=False))
    average_trade_latency: float = Field(sa_column=Column(Float, nullable=False))
    min_trade_latency: float = Field(sa_column=Column(Float, nullable=False))
    max_trade_latency: float = Field(sa_column=Column(Float, nullable=False))
    total_trade_volume_in_quote: float = Field(sa_column=Column(Float, nullable=False))
