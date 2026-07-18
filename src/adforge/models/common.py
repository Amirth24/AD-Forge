"""Shared enumerations and primitives."""

from enum import IntEnum, StrEnum


class Status(StrEnum):
    """Generic lifecycle status."""

    DRAFT = "draft"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    CLOSED = "closed"


class Complexity(IntEnum):
    """Rough complexity scoring for sub-problems."""

    LOW = 1
    MEDIUM = 3
    HIGH = 5
    EXTREME = 8
