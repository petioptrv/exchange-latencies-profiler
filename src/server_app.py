from threading import Thread
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.api.main import api_router
from src.background_fetcher import BackgroundRefresher
from src.config import settings
from src.logging_utils import setup_logging

setup_logging()


@asynccontextmanager
async def lifespan(_: FastAPI):
    background_fetcher = BackgroundRefresher()
    t = Thread(target=background_fetcher.refresher_loop, name="data-cache-refresher", daemon=True)
    t.start()

    yield

    background_fetcher.stop()
    t.join()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80, log_level="info")
