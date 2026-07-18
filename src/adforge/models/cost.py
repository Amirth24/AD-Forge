"""Cost/price line items and summaries."""

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class CostLineItem(BaseModel):
    """A single priced component of a solution."""

    id: str = Field(default_factory=lambda: uuid4().hex)
    solution_id: str
    sub_problem_id: str | None = None
    provider: str
    service: str
    region: str = ""
    parameters: dict[str, Any] = Field(default_factory=dict)
    unit_price: Decimal
    quantity: Decimal = Decimal("1")
    unit: str = ""
    source_url: str = ""
    source_fetched_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def total(self) -> Decimal:
        """Total cost for this line item."""
        return self.unit_price * self.quantity


class CostSummary(BaseModel):
    """Aggregated cost view attached to a solution document."""

    currency: str = "USD"
    total_monthly: Decimal = Decimal("0")
    total_hourly: Decimal | None = None
    line_item_count: int = 0
    providers: list[str] = Field(default_factory=list)
    note: str = ""
