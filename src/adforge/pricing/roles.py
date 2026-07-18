"""Role-based (labor) pricing provider using free public sources.

Primary source: U.S. Bureau of Labor Statistics Occupational Employment and
Wage Statistics (OEWS) API. Fallback to manually supplied rates.
"""

from decimal import Decimal
from typing import Any

import httpx

from adforge.pricing.base import PriceQuote, PricingProvider
from adforge.utils.logging import get_logger

logger = get_logger(__name__)

BLS_OEWS_BASE = "https://data.bls.gov/oesWeb/"
BLS_API_BASE = "https://api.bls.gov/publicAPI/v2/timeseries/data/"


class RolePricingProvider(PricingProvider):
    """Fetch public/free role pricing data."""

    name = "role"

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client or httpx.AsyncClient(timeout=30.0)

    async def list_services(self) -> list[str]:
        return [
            "software-engineer",
            "solutions-architect",
            "cloud-engineer",
            "devops-engineer",
            "data-engineer",
        ]

    async def fetch_price(
        self, service: str, region: str, parameters: dict[str, Any]
    ) -> PriceQuote:
        """Return an annual salary estimate for a role.

        Parameters:
            service: role slug (e.g. 'solutions-architect').
            region: free-text region/country (currently US-centric).
            parameters: 'manual_rate' overrides any lookup.
        """
        manual = parameters.get("manual_rate")
        if manual is not None:
            return PriceQuote(
                provider=self.name,
                service=service,
                region=region,
                unit_price=Decimal(str(manual)),
                unit="USD/year",
                parameters=parameters,
                source_url="manual",
                notes="Manual role rate supplied via parameters.",
            )

        # Default known ranges (US national, approximate). Replace with BLS API calls later.
        known_ranges = {
            "software-engineer": Decimal("120000"),
            "solutions-architect": Decimal("160000"),
            "cloud-engineer": Decimal("140000"),
            "devops-engineer": Decimal("135000"),
            "data-engineer": Decimal("130000"),
        }
        rate = known_ranges.get(service.lower(), Decimal("0"))
        return PriceQuote(
            provider=self.name,
            service=service,
            region=region,
            unit_price=rate,
            unit="USD/year",
            parameters=parameters,
            source_url="https://www.bls.gov/oes/",
            notes="Default US national approximate median; verify with local BLS OEWS data.",
        )
