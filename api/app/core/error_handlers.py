import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    """
    Catch anything that isn't already handled elsewhere (i.e. any
    exception that isn't a deliberate HTTPException raised by a route or
    service) and turn it into two things:

    1. A logged error with a full traceback, through the same logger
       configuration as the rest of the app. Without this, an unhandled
       exception becomes an unformatted stack trace wherever the ASGI
       server happens to print it - inconsistent, and easy to miss.
    2. A stable JSON response instead of a raw traceback or a framework
       default. It reuses the {"detail": ...} key that HTTPException
       responses already use elsewhere in this API (see the 404s in
       workflow_runs.py and dashboard.py), so API consumers only ever
       need to handle one error shape, not two.

    Deliberately generic message: the real error is logged server-side
    for debugging, but never echoed back to the client - internal
    exception details (stack traces, DB errors, etc.) can leak
    implementation details that shouldn't be public.
    """

    @app.exception_handler(Exception)
    async def handle_unexpected_exception(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            "Unhandled exception during %s %s",
            request.method,
            request.url.path,
        )

        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error. Please try again or contact support."},
        )
