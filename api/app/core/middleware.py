import logging
import time

from fastapi import FastAPI, Request

logger = logging.getLogger("app.request")


def register_request_logging(app: FastAPI) -> None:
    """
    Logs one line per request: method, path, status code, and how long it
    took. This is the minimum useful observability for an API - enough to
    answer "what's slow?" and "what's failing?" from logs alone, without
    needing a dedicated APM/tracing tool for a project at this scale.
    """

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.perf_counter()

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "%s %s -> %s (%.1fms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        return response
