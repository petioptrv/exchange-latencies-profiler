from typing import Tuple, List

from pydantic import BaseModel


class DataResponse(BaseModel):
    location: str
    coords: Tuple[float, float]
    latestLatency: float
    latencies: List[Tuple[float, float]]
    volume: List[Tuple[float, float]]
