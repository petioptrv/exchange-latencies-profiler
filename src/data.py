from pydantic import BaseModel


class TradeReceipt(BaseModel):
    id: str
    timestamp: float
    latency: float
    volume_in_quote: float


class ProfilerInstanceSpec(BaseModel):
    symbol: str
    cloud_instance_id: int
    exchange_id: int
