from typing import List

from fastapi import APIRouter

from src.api.responses import DataResponse
from src.cache_manager import cache

router = APIRouter(prefix="/utils", tags=["utils"])


@router.get("/health-check/")
async def health_check() -> bool:
    return True


@router.get("/data", response_model=List[DataResponse])
async def data():
    data_ = cache.get()
    return data_
