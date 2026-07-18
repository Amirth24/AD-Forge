"""AWS pricing provider.

Uses the AWS Price List Query API via boto3. This API requires valid AWS
credentials (IAM permission ``pricing:GetProducts``), but the pricing data itself
is public. To avoid triggering boto3 credential provider chains that depend on
``botocore[crt]`` (e.g. AWS CLI ``aws login`` profiles), the client is built
lazily from explicit environment credentials only.
"""

import os
from decimal import Decimal
from typing import Any

import boto3  # type: ignore[import-untyped]
from botocore.config import Config  # type: ignore[import-untyped]
from botocore.exceptions import NoCredentialsError  # type: ignore[import-untyped]

from adforge.pricing.base import PriceQuote, PricingProvider
from adforge.utils.logging import get_logger

logger = get_logger(__name__)

AWS_PRICING_REGION = os.environ.get("AWS_PRICING_REGION", "us-east-1")


class AWSPricingProvider(PricingProvider):
    """Fetch AWS pricing for common compute/storage services."""

    name = "aws"

    def __init__(self, region: str | None = None) -> None:
        self._region = region or AWS_PRICING_REGION
        self._client = None

    def _get_client(self) -> Any:
        """Lazy-build a pricing client using explicit env credentials.

        This bypasses boto3's default credential provider chain, which can fail
        with a ``botocore[crt]`` dependency error when the host has an
        ``aws login`` profile configured.
        """
        if self._client is None:
            access_key = os.environ.get("AWS_ACCESS_KEY_ID")
            secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
            session_token = os.environ.get("AWS_SESSION_TOKEN")
            if not access_key or not secret_key:
                raise NoCredentialsError(
                    service_name="pricing",
                    error_message=(
                        "AWS pricing requires AWS_ACCESS_KEY_ID and "
                        "AWS_SECRET_ACCESS_KEY. The AWS Price List Query API "
                        "does not support anonymous requests."
                    ),
                )
            session = boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                aws_session_token=session_token,
            )
            self._client = session.client(
                "pricing",
                region_name="us-east-1",
                config=Config(retries={"max_attempts": 3, "mode": "adaptive"}),
            )
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
        prices: list[Decimal] = []
        unit = ""
        source_url = "https://aws.amazon.com/pricing/"
        notes: str = ""

        try:
            paginator = self._get_client().get_paginator("get_products")
            for page in paginator.paginate(ServiceCode=service_code, Filters=filters):
                for price_item in page.get("PriceList", []):
                    try:
                        on_demand = _extract_on_demand_rate(price_item)
                        if on_demand:
                            prices.append(on_demand["price"])
                            unit = on_demand["unit"]
                    except Exception as exc:  # noqa: BLE001
                        logger.debug("Could not parse AWS price item", error=str(exc))
        except NoCredentialsError as exc:
            logger.warning("AWS credentials not available", error=str(exc))
            notes = (
                "AWS pricing skipped: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY "
                "are required for the AWS Price List Query API."
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("AWS pricing query failed", error=str(exc))
            notes = f"AWS pricing query failed: {exc}"

        if not prices:
            return PriceQuote(
                provider=self.name,
                service=service_code,
                region=region,
                unit_price=Decimal("0"),
                unit="",
                parameters=parameters,
                source_url=source_url,
                notes=notes or "No On-Demand price found for the given filters.",
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
