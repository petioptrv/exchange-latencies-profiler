from pydantic import BaseModel

from src.db.model import CloudInstance, Exchange


class TradeReceipt(BaseModel):
    id: str
    timestamp: float
    latency: float
    volume: float


class ProfilerInstanceSpec(BaseModel):
    symbol: str
    cloud_instance: CloudInstance
    exchange: Exchange
