from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.core.config import settings
from app.api.routes.tickets import router as tickets_router
from app.api.routes.webhooks import router as webhooks_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend API for automating IT ticket triage, routing, and notifications."
)

app.include_router(health_router)
app.include_router(tickets_router)
app.include_router(webhooks_router)