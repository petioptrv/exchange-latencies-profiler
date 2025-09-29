from typing import List

from fastapi import APIRouter

from src.api.deps import SessionDep
from src.api.responses import DataResponse
from src.config import settings
from src.db.crud import get_all_historical_minute_trade_latencies
from src.db.model import HistoricalMinuteTradeLatenciesEntry

router = APIRouter(prefix="/utils", tags=["utils"])


@router.get("/health-check/")
async def health_check() -> bool:
    return True


@router.get("/data", response_model=List[DataResponse])
async def data(session: SessionDep):
    entries: List[HistoricalMinuteTradeLatenciesEntry] = get_all_historical_minute_trade_latencies(session=session)
    latencies = []
    volume = []
    for entry in entries:
        timestamp = entry.timestamp.timestamp()
        latencies.append((entry.average_trade_latency * 1e3, timestamp))
        volume.append((entry.total_trade_volume_in_quote * 1e3, timestamp))
    response = [
        DataResponse(
            location=settings.CLOUD_LOCATION,
            coords=(settings.CLOUD_LOCATION_LONGITUDE, settings.CLOUD_LOCATION_LATITUDE),
            latestLatency=entries[-1].average_trade_latency * 1e3,
            latencies=latencies,
            volume=volume,
        )
    ]
    return response
