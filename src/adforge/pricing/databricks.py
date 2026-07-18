"""Databricks pricing provider (stub).

Databricks pricing is not published as a public query API. This provider accepts
manual rates and can be extended with a real API client once credentials or an
official endpoint are available.
"""

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from adforge.pricing.base import PriceQuote, PricingProvider


class DatabricksPricingProvider(PricingProvider):
    """Stub provider for Databricks prices."""

    name = "databricks"

    async def list_services(self) -> list[str]:
        return ["jobs-compute", "sql-warehouse", "all-purpose-compute", "dbtu"]

    async def fetch_price(
        self, service: str, region: str, parameters: dict[str, Any]
    ) -> PriceQuote:
        manual = parameters.get("manual_rate")
        unit = parameters.get("manual_unit", "DBU/hour")
        if manual is None:
            return PriceQuote(
                provider=self.name,
                service=service,
                region=region,
                unit_price=Decimal("0"),
                unit=unit,
                parameters=parameters,
                source_url="https://www.databricks.com/product/pricing",
                notes=(
                    "Databricks pricing requires a manual_rate in parameters"
                    " until an API is available."
                ),
            )
        return PriceQuote(
            provider=self.name,
            service=service,
            region=region,
            unit_price=Decimal(str(manual)),
            unit=unit,
            parameters=parameters,
            source_url="https://www.databricks.com/product/pricing",
            source_fetched_at=datetime.now(UTC),
            notes="Manual Databricks rate supplied via parameters.",
        )
