"""Pricing provider interface and shared models."""

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class PriceQuote(BaseModel):
    """A single normalized price quote from any provider."""

    provider: str
    service: str
    region: str
    unit_price: Decimal
    unit: str = ""
    parameters: dict[str, Any] = Field(default_factory=dict)
    source_url: str = ""
    source_fetched_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    notes: str = ""


class PricingProvider(ABC):
    """Abstract base class for pricing providers."""

    name: str = ""

    @abstractmethod
    async def fetch_price(
        self, service: str, region: str, parameters: dict[str, Any]
    ) -> PriceQuote:
        """Return a price quote for the given service/region/parameters."""
        ...

    async def list_services(self) -> list[str]:
        """Optional: return known services for this provider."""
        return []
