"""Attach cost line items to solutions and summarize."""

import json
from decimal import Decimal
from typing import Any

from mcp.types import TextContent, Tool

from adforge.models import CostLineItem, CostSummary
from adforge.persistence import CostRepository, SolutionRepository
from adforge.pricing import PricingManager
from adforge.tools import registry


def _cost_repo() -> CostRepository:
    return CostRepository()


def _solution_repo() -> SolutionRepository:
    return SolutionRepository()


_manager = PricingManager()


async def _attach_cost_to_solution(arguments: dict[str, Any]) -> list[TextContent]:
    solution_id = arguments["solution_id"]
    if _solution_repo().get(solution_id) is None:
        return [TextContent(type="text", text=f"Solution not found: {solution_id}")]

    provider = arguments["provider"]
    service = arguments["service"]
    region = arguments.get("region", "")
    parameters = json.loads(arguments.get("parameters_json", "{}"))
    quantity = Decimal(str(arguments.get("quantity", "1")))
    sub_problem_id = arguments.get("sub_problem_id")

    quote = await _manager.fetch_price(provider, service, region, parameters)
    item = _cost_repo().save(
        CostLineItem(
            solution_id=solution_id,
            sub_problem_id=sub_problem_id,
            provider=quote.provider,
            service=quote.service,
            region=quote.region,
            parameters=quote.parameters,
            unit_price=quote.unit_price,
            quantity=quantity,
            unit=quote.unit,
            source_url=quote.source_url,
            source_fetched_at=quote.source_fetched_at,
        )
    )
    return [TextContent(type="text", text=item.model_dump_json())]


async def _summarize_solution_cost(arguments: dict[str, Any]) -> list[TextContent]:
    solution_id = arguments["solution_id"]
    items = _cost_repo().list_for_solution(solution_id)
    if not items:
        return [TextContent(type="text", text=f"No cost line items for solution {solution_id}")]

    total = sum((item.total for item in items), Decimal("0"))
    providers = sorted({item.provider for item in items})
    summary = CostSummary(
        currency="USD",
        total_monthly=total,
        line_item_count=len(items),
        providers=providers,
        note="Rolled up from stored cost line items.",
    )

    solution = _solution_repo().get(solution_id)
    if solution is not None:
        solution.cost_summary = summary
        _solution_repo().save(solution)

    return [TextContent(type="text", text=summary.model_dump_json())]


registry.register(
    Tool(
        name="attach_cost_to_solution",
        description="Fetch a price and attach it as a cost line item to a solution.",
        inputSchema={
            "type": "object",
            "properties": {
                "solution_id": {"type": "string"},
                "sub_problem_id": {
                    "type": "string",
                    "description": "Optional sub-problem this cost belongs to",
                },
                "provider": {
                    "type": "string",
                    "enum": ["aws", "azure", "gcp", "databricks", "role"],
                },
                "service": {"type": "string"},
                "region": {"type": "string"},
                "parameters_json": {
                    "type": "string",
                    "description": "JSON provider-specific filters",
                },
                "quantity": {
                    "type": "string",
                    "description": "Decimal quantity (e.g. '2' or '730' hours/month)",
                },
            },
            "required": ["solution_id", "provider", "service", "region"],
        },
    ),
    _attach_cost_to_solution,
)

registry.register(
    Tool(
        name="summarize_solution_cost",
        description="Roll up all cost line items for a solution and store the summary.",
        inputSchema={
            "type": "object",
            "properties": {"solution_id": {"type": "string"}},
            "required": ["solution_id"],
        },
    ),
    _summarize_solution_cost,
)
