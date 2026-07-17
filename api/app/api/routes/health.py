from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    """
    Liveness check: is the process running and able to respond to HTTP at
    all? Deliberately has zero dependencies - no database, no external
    calls. A liveness check that depends on the database answers the
    wrong question: if the app process is fine but the database is down,
    restarting the container (what a failed liveness check triggers)
    won't fix anything, it just adds downtime on top of the outage.
    That's what /health/ready below is for.
    """
    return {
        "status": "healthy",
        "service": "AI IT Ticket Automation Platform API",
        "version": settings.app_version,
        "environment": settings.environment,
    }


@router.get("/health/ready")
def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness check: can this instance actually serve requests right now?
    Unlike /health, this deliberately DOES check the database, since
    nearly every real endpoint in this app needs one. Deployment
    platforms use readiness (not liveness) to decide whether to route
    traffic to an instance - a container can be "alive" while still not
    ready to serve requests, e.g. during database startup or after the
    connection pool is exhausted.

    Catches SQLAlchemyError specifically, not Exception broadly: a
    genuinely unexpected bug here should still hit the global exception
    handler and get logged as a real bug, not get silently mislabeled as
    "database unavailable".
    """
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "reason": "database_unavailable"},
        )

    return {"status": "ready"}
