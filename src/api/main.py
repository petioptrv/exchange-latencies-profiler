from fastapi import APIRouter

from src.api import routes

api_router = APIRouter()
api_router.include_router(routes.router)
