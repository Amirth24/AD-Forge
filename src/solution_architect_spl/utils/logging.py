"""Structured logging setup."""

import structlog


def get_logger(name: str):
    """Return a structlog logger for the given module name."""
    return structlog.get_logger(name)
