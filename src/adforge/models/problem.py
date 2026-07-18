"""Problem statement model."""

from datetime import UTC, datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class Problem(BaseModel):
    """A problem to be solved by one or more solution approaches."""

    id: str = Field(default_factory=lambda: uuid4().hex)
    title: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(UTC)
