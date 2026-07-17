import logging
import sys

from app.core.config import settings


def configure_logging() -> None:
    # settings.log_level comes from the LOG_LEVEL env var (defaults to
    # "INFO"). Python's logging module accepts level names as strings
    # directly, so no mapping to logging.INFO/DEBUG/etc. is needed here.
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
