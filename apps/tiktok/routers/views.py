from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from core.settings import settings
from core.database.dependencies import SessionDep
from apps.tiktok.routers.api import get_campaign_history_data

router = APIRouter(tags=["web"])

templates = settings.templates

@router.get("/")
async def campaign_history_page(request: Request):
    return templates.TemplateResponse(request, "campaign_history.html", {})
