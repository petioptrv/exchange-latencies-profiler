import uvicorn
from fastapi import FastAPI

from src.api.main import api_router
from src.config import settings
from src.logging_config import setup_logging

setup_logging()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"/openapi.json",
)

app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")
