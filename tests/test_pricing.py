"""Tests for pricing providers and manager."""

import re
from decimal import Decimal

import pytest
from pytest_httpx import HTTPXMock

from adforge.pricing import AzurePricingProvider, PricingManager, RolePricingProvider


@pytest.mark.asyncio
async def test_azure_provider_parses_retail_price(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url=re.compile(r"https://prices\.azure\.com/api/retail/prices.*"),
        json={
            "Items": [
                {
                    "serviceName": "Virtual Machines",
                    "armRegionName": "eastus",
                    "skuName": "D2s_v5",
                    "retailPrice": 0.096,
                    "unitOfMeasure": "1 Hour",
                }
            ]
        },
    )
    provider = AzurePricingProvider()
    quote = await provider.fetch_price("Virtual Machines", "eastus", {"skuName": "D2s_v5"})
    assert quote.provider == "azure"
    assert quote.unit_price == Decimal("0.096")
    assert quote.unit == "1 Hour"


@pytest.mark.asyncio
async def test_azure_provider_handles_empty_response(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url=re.compile(r"https://prices\.azure\.com/api/retail/prices.*"),
        json={"Items": []},
    )
    provider = AzurePricingProvider()
    quote = await provider.fetch_price("Storage", "eastus", {})
    assert quote.unit_price == Decimal("0")


@pytest.mark.asyncio
async def test_role_provider_manual_rate():
    provider = RolePricingProvider()
    quote = await provider.fetch_price("solutions-architect", "us", {"manual_rate": "175000"})
    assert quote.unit_price == Decimal("175000")
    assert quote.unit == "USD/year"


@pytest.mark.asyncio
async def test_role_provider_default():
    provider = RolePricingProvider()
    quote = await provider.fetch_price("solutions-architect", "us", {})
    assert quote.unit_price > Decimal("0")
    assert quote.unit == "USD/year"


@pytest.mark.asyncio
async def test_manager_lists_providers():
    manager = PricingManager()
    providers = manager.list_providers()
    assert "aws" in providers
    assert "azure" in providers
    assert "role" in providers
