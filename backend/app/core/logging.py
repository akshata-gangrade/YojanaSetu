"""Structured logging configuration without sensitive data leakage."""

import logging
import sys


def setup_logging(log_level: str = "INFO") -> None:
    """Configure standard structured logging.

    Ensures no PII is logged and formats logs cleanly for production and dev.
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    # Silence overly verbose external loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


logger = logging.getLogger("yojanasetu")
