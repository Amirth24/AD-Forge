"""Provider manager and dispatch."""

from typing import Any

from adforge.pricing.aws import AWSPricingProvider
from adforge.pricing.azure import AzurePricingProvider
from adforge.pricing.base import PriceQuote, PricingProvider
from adforge.pricing.databricks import DatabricksPricingProvider
from adforge.pricing.gcp import GCPPricingProvider
from adforge.pricing.roles import RolePricingProvider


class PricingManager:
    """Thin dispatcher across pricing providers."""

    def __init__(self) -> None:
        self._providers: dict[str, PricingProvider] = {
            "aws": AWSPricingProvider(),
            "azure": AzurePricingProvider(),
            "gcp": GCPPricingProvider(),
            "databricks": DatabricksPricingProvider(),
            "role": RolePricingProvider(),
        }

    def get_provider(self, name: str) -> PricingProvider:
        try:
            return self._providers[name.lower()]
        except KeyError as exc:
            raise ValueError(f"Unknown pricing provider: {name}") from exc

    async def fetch_price(
        self, provider: str, service: str, region: str, parameters: dict[str, Any]
    ) -> PriceQuote:
        return await self.get_provider(provider).fetch_price(service, region, parameters)

    def list_providers(self) -> list[str]:
        return list(self._providers.keys())

    async def list_services(self, provider: str) -> list[str]:
        return await self.get_provider(provider).list_services()
