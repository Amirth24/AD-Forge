"""AWS public pricing provider.

Uses the AWS Price List Query API via boto3. No account credentials are required;
the public endpoint is reached by configuring the pricing client against
us-east-1.
"""

import os
from decimal import Decimal
from typing import Any

import boto3  # type: ignore[import-untyped]
from botocore.config import Config  # type: ignore[import-untyped]
from botocore.handlers import disable_signing  # type: ignore[import-untyped]

from adforge.pricing.base import PriceQuote, PricingProvider
from adforge.utils.logging import get_logger

logger = get_logger(__name__)

AWS_PRICING_REGION = os.environ.get("AWS_PRICING_REGION", "us-east-1")


class AWSPricingProvider(PricingProvider):
    """Fetch public AWS pricing for common compute/storage services."""

    name = "aws"

    def __init__(self, region: str | None = None) -> None:
        self._region = region or AWS_PRICING_REGION
        self._client = None

    def _get_client(self) -> Any:
        """Lazy-build an unsigned pricing client so import time does not need credentials."""
        if self._client is None:
            # The AWS Pricing API is public and unsigned, so real credentials are
            # unnecessary. Provide dummy keys to short-circuit boto3's credential
            # provider chain, avoiding environments that try to load SSO/WebIdentity
            # providers which require botocore[crt].
            session = boto3.Session(
                aws_access_key_id="adforge",
                aws_secret_access_key="adforge",
            )
            client = session.client(
                "pricing",
                region_name="us-east-1",
                config=Config(retries={"max_attempts": 3, "mode": "adaptive"}),
            )
            client.meta.events.register("choose-signer.pricing.*", disable_signing)
            self._client = client
        return self._client

    async def list_services(self) -> list[str]:
        """Return known AWS service codes we can price."""
        return [
            "AmazonEC2",
            "AmazonS3",
            "AWSLambda",
            "AmazonRDS",
            "AmazonDynamoDB",
            "AmazonCloudWatch",
        ]

    async def fetch_price(
        self, service: str, region: str, parameters: dict[str, Any]
    ) -> PriceQuote:
        """Look up a public AWS price for a service/region.

        Parameters:
            service: AWS service code (e.g. AmazonEC2) or friendly name.
            region: AWS region name (e.g. us-east-1).
            parameters: extra filters such as instanceType, operatingSystem,
                storageClass, etc.
        """
        service_code = _normalize_service_code(service)
        filters = [{"Field": "location", "Type": "TERM_MATCH", "Value": _region_name(region)}]
        for key, value in parameters.items():
            filters.append({"Field": key, "Type": "TERM_MATCH", "Value": str(value)})

        logger.info("Querying AWS pricing", service=service_code, region=region)
        paginator = self._get_client().get_paginator("get_products")
        prices: list[Decimal] = []
        unit = ""
        source_url = "https://aws.amazon.com/pricing/"

        for page in paginator.paginate(ServiceCode=service_code, Filters=filters):
            for price_item in page.get("PriceList", []):
                try:
                    on_demand = _extract_on_demand_rate(price_item)
                    if on_demand:
                        prices.append(on_demand["price"])
                        unit = on_demand["unit"]
                except Exception as exc:  # noqa: BLE001
                    logger.debug("Could not parse AWS price item", error=str(exc))

        if not prices:
            return PriceQuote(
                provider=self.name,
                service=service_code,
                region=region,
                unit_price=Decimal("0"),
                unit="",
                parameters=parameters,
                source_url=source_url,
                notes="No public On-Demand price found for the given filters.",
            )

        best = min(prices)
        return PriceQuote(
            provider=self.name,
            service=service_code,
            region=region,
            unit_price=best,
            unit=unit,
            parameters=parameters,
            source_url=source_url,
            notes=f"Lowest On-Demand rate from {len(prices)} matching SKU(s).",
        )


def _normalize_service_code(service: str) -> str:
    """Map friendly names to AWS service codes."""
    mapping = {
        "ec2": "AmazonEC2",
        "s3": "AmazonS3",
        "lambda": "AWSLambda",
        "rds": "AmazonRDS",
        "dynamodb": "AmazonDynamoDB",
        "cloudwatch": "AmazonCloudWatch",
    }
    return mapping.get(service.lower(), service)


def _region_name(region_code: str) -> str:
    """Best-effort mapping of AWS region code to the location string used by pricing API."""
    mapping = {
        "us-east-1": "US East (N. Virginia)",
        "us-east-2": "US East (Ohio)",
        "us-west-1": "US West (N. California)",
        "us-west-2": "US West (Oregon)",
        "eu-west-1": "EU (Ireland)",
        "eu-central-1": "EU (Frankfurt)",
        "ap-south-1": "Asia Pacific (Mumbai)",
        "ap-southeast-1": "Asia Pacific (Singapore)",
    }
    return mapping.get(region_code, region_code)


def _extract_on_demand_rate(price_item: Any) -> dict[str, Any] | None:
    """Parse the boto3 price list JSON to find the first OnDemand rate."""
    terms = price_item.get("terms", {}).get("OnDemand", {})
    for term in terms.values():
        for dimension in term.get("priceDimensions", {}).values():
            price = dimension.get("pricePerUnit", {})
            usd = price.get("USD")
            if usd:
                return {"price": Decimal(usd), "unit": dimension.get("unit", "")}
    return None
