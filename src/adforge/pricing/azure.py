"""Azure Retail Prices API provider."""

from decimal import Decimal
from typing import Any

import httpx

from adforge.pricing.base import PriceQuote, PricingProvider
from adforge.utils.logging import get_logger

logger = get_logger(__name__)

AZURE_RETAIL_BASE = "https://prices.azure.com/api/retail/prices"


class AzurePricingProvider(PricingProvider):
    """Fetch public Azure retail prices."""

    name = "azure"

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client or httpx.AsyncClient(timeout=30.0)

    async def list_services(self) -> list[str]:
        return [
            "Virtual Machines",
            "Storage",
            "Azure SQL Database",
            "Azure Functions",
            "Azure Monitor",
            "Azure Blob Storage",
        ]

    async def fetch_price(
        self, service: str, region: str, parameters: dict[str, Any]
    ) -> PriceQuote:
        """Look up Azure retail price for a service/region.

        Parameters:
            service: Azure serviceName (e.g. 'Virtual Machines', 'Storage').
            region: Azure armRegionName (e.g. eastus).
            parameters: extra filters such as skuName, productName.
        """
        filters = [
            f"serviceName eq '{service}'",
            f"armRegionName eq '{region}'",
        ]
        for key, value in parameters.items():
            filters.append(f"{key} eq '{value}'")

        query = " and ".join(filters)
        url = f"{AZURE_RETAIL_BASE}?$filter={query}"
        logger.info("Querying Azure retail prices", service=service, region=region)

        try:
            response = await self._client.get(url)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Azure retail price query failed", error=str(exc))
            return PriceQuote(
                provider=self.name,
                service=service,
                region=region,
                unit_price=Decimal("0"),
                parameters=parameters,
                source_url=url,
                notes=f"Azure API request failed: {exc}",
            )

        data = response.json()
        items = data.get("Items", [])
        if not items:
            return PriceQuote(
                provider=self.name,
                service=service,
                region=region,
                unit_price=Decimal("0"),
                parameters=parameters,
                source_url=url,
                notes="No matching Azure retail price found.",
            )

        item = items[0]
        unit_price = Decimal(str(item.get("retailPrice", 0)))
        unit = item.get("unitOfMeasure", "")
        return PriceQuote(
            provider=self.name,
            service=service,
            region=region,
            unit_price=unit_price,
            unit=unit,
            parameters=parameters,
            source_url=url,
            notes=f"Returned {len(items)} matching SKU(s); using first.",
        )
