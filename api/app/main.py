from fastapi import FastAPI

from app.api.routes.health import router as health_router

app = FastAPI(
    title="AI IT Ticket Automation Platform API",
    version="0.1.0",
    description="Backend API for automating IT ticket triage, routing, and notifications."
)

app.include_router(health_router)