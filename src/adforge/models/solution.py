"""Solution document model, shaped like a GitHub PR/issue."""

from datetime import UTC, datetime
from uuid import uuid4

from pydantic import BaseModel, Field

from adforge.models.common import Status
from adforge.models.cost import CostSummary


class Comment(BaseModel):
    """A comment on a solution, like a GitHub issue comment."""

    id: str = Field(default_factory=lambda: uuid4().hex)
    author: str = ""
    body: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Review(BaseModel):
    """A review/approval record on a solution, like a GitHub PR review."""

    id: str = Field(default_factory=lambda: uuid4().hex)
    author: str = ""
    state: str = "commented"  # commented, approved, changes_requested
    body: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Solution(BaseModel):
    """A solution approach for a problem, persisted as a PR/issue-shaped document."""

    id: str = Field(default_factory=lambda: uuid4().hex)
    problem_id: str
    title: str
    status: Status = Status.DRAFT
    body: str = ""
    comments: list[Comment] = Field(default_factory=list)
    reviews: list[Review] = Field(default_factory=list)
    labels: list[str] = Field(default_factory=list)
    assignees: list[str] = Field(default_factory=list)
    cost_summary: CostSummary | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(UTC)
