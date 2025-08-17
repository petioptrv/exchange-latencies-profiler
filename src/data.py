from pydantic import BaseModel


class TradeReceipt(BaseModel):
    id: str
    timestamp: float
    latency: float
    volume: float
