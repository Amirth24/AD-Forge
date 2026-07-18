"""GCP pricing provider (stub).

GCP does not expose a single unauthenticated public pricing query API equivalent
to AWS/Azure. This provider provides a cacheable interface and can be wired to a
Cloud Billing Catalog API key later.
"""

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from adforge.pricing.base import PriceQuote, PricingProvider


class GCPPricingProvider(PricingProvider):
    """Stub provider for GCP prices."""

    name = "gcp"

    async def list_services(self) -> list[str]:
        return ["compute", "storage", "bigquery", "cloud-run", "cloud-sql"]

    async def fetch_price(
        self, service: str, region: str, parameters: dict[str, Any]
    ) -> PriceQuote:
        # Placeholder: require an explicit manual_rate in parameters to return anything.
        manual = parameters.get("manual_rate")
        unit = parameters.get("manual_unit", "")
        if manual is None:
            return PriceQuote(
                provider=self.name,
                service=service,
                region=region,
                unit_price=Decimal("0"),
                unit=unit,
                parameters=parameters,
                source_url="https://cloud.google.com/pricing",
                notes=(
                    "GCP public pricing is not available without a Cloud Billing API key."
                    " Provide manual_rate to use a stub value."
                ),
            )
        return PriceQuote(
            provider=self.name,
            service=service,
            region=region,
            unit_price=Decimal(str(manual)),
            unit=unit,
            parameters=parameters,
            source_url="https://cloud.google.com/pricing",
            source_fetched_at=datetime.now(UTC),
            notes="Manual rate supplied via parameters.",
        )
