from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AI IT Ticket Automation Platform API",
        "version": settings.app_version,
        "environment": settings.environment
    }