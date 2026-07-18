"""Sub-problem model for divide-and-conquer decomposition."""

from datetime import UTC, datetime
from uuid import uuid4

from pydantic import BaseModel, Field

from adforge.models.common import Complexity, Status


class SubProblem(BaseModel):
    """A sub-problem belonging to a problem and optionally a solution."""

    id: str = Field(default_factory=lambda: uuid4().hex)
    problem_id: str
    solution_id: str | None = None
    parent_id: str | None = None
    title: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    complexity: Complexity = Complexity.MEDIUM
    status: Status = Status.DRAFT
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(UTC)
