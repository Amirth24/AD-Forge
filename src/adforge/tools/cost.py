"""Pricing/cost MCP tools."""

import json
from typing import Any

from mcp.types import TextContent, Tool

from adforge.persistence.repositories.cost_repository import PricingCache
from adforge.pricing import PricingManager
from adforge.tools import registry

_manager = PricingManager()


def _cache() -> PricingCache:
    import os

    ttl = int(os.environ.get("ADFORGE_CACHE_TTL", "86400"))
    return PricingCache(ttl_seconds=ttl)


async def _estimate_cost(arguments: dict[str, Any]) -> list[TextContent]:
    provider = arguments["provider"]
    service = arguments["service"]
    region = arguments.get("region", "")
    parameters = json.loads(arguments.get("parameters_json", "{}"))

    cache = _cache()
    cached = cache.get(provider, service, region, parameters)
    if cached is not None:
        return [TextContent(type="text", text=json.dumps(cached))]

    quote = await _manager.fetch_price(provider, service, region, parameters)
    cache.set(provider, service, region, parameters, quote.model_dump(mode="json"))
    return [TextContent(type="text", text=quote.model_dump_json())]


async def _list_pricing_providers(arguments: dict[str, Any]) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps(_manager.list_providers()))]


async def _list_pricing_services(arguments: dict[str, Any]) -> list[TextContent]:
    provider = arguments["provider"]
    services = await _manager.list_services(provider)
    return [TextContent(type="text", text=json.dumps(services))]


registry.register(
    Tool(
        name="estimate_cost",
        description="Estimate the unit price for a cloud service/role from a provider.",
        inputSchema={
            "type": "object",
            "properties": {
                "provider": {
                    "type": "string",
                    "enum": ["aws", "azure", "gcp", "databricks", "role"],
                    "description": "Pricing provider to query",
                },
                "service": {"type": "string", "description": "Service or role name"},
                "region": {"type": "string", "description": "Region or location"},
                "parameters_json": {
                    "type": "string",
                    "description": (
                        "JSON object of provider-specific filters"
                        " (e.g. instanceType, skuName, manual_rate)"
                    ),
                },
            },
            "required": ["provider", "service", "region"],
        },
    ),
    _estimate_cost,
)

registry.register(
    Tool(
        name="list_pricing_providers",
        description="List available pricing providers.",
        inputSchema={"type": "object", "properties": {}},
    ),
    _list_pricing_providers,
)

registry.register(
    Tool(
        name="list_pricing_services",
        description="List known services for a pricing provider.",
        inputSchema={
            "type": "object",
            "properties": {
                "provider": {
                    "type": "string",
                    "enum": ["aws", "azure", "gcp", "databricks", "role"],
                }
            },
            "required": ["provider"],
        },
    ),
    _list_pricing_services,
)
