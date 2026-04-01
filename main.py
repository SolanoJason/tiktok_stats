from core.database import load_models, engine
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware

from apps.tiktok.routers.api import router as tiktok_api_router
from apps.tiktok.routers.views import router as tiktok_views_router

load_models()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

api_router = APIRouter(prefix="/api")

web_router = APIRouter(tags=["web"])

api_router.include_router(tiktok_api_router)
web_router.include_router(tiktok_views_router)

app.include_router(api_router)
app.include_router(web_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(GZipMiddleware)