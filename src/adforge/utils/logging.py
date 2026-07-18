"""Structured logging setup."""

from typing import Any

import structlog


def get_logger(name: str) -> Any:
    """Return a structlog logger for the given module name."""
    return structlog.get_logger(name)
