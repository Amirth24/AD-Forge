"""Integration tests for MCP tools."""

import json

import pytest

from adforge.tools.cost import _estimate_cost
from adforge.tools.decompose import _decompose_problem
from adforge.tools.problem import _create_problem, _get_problem
from adforge.tools.solution import _create_solution, _get_solution
from adforge.tools.solution_cost import (
    _attach_cost_to_solution,
    _summarize_solution_cost,
)


@pytest.mark.asyncio
async def test_create_and_get_problem(fresh_db):
    result = await _create_problem(
        {"title": "Build API", "description": "REST API", "tags_csv": "api,aws"}
    )
    problem = json.loads(result[0].text)
    assert problem["title"] == "Build API"
    assert problem["tags"] == ["api", "aws"]

    fetched = await _get_problem({"problem_id": problem["id"]})
    data = json.loads(fetched[0].text)
    assert data["id"] == problem["id"]


@pytest.mark.asyncio
async def test_create_solution(fresh_db):
    problem_result = await _create_problem({"title": "P"})
    problem = json.loads(problem_result[0].text)

    solution_result = await _create_solution({"problem_id": problem["id"], "title": "S1"})
    solution = json.loads(solution_result[0].text)
    assert solution["problem_id"] == problem["id"]
    assert solution["status"] == "draft"

    fetched = await _get_solution({"solution_id": solution["id"]})
    assert json.loads(fetched[0].text)["title"] == "S1"


@pytest.mark.asyncio
async def test_decompose_problem(fresh_db):
    problem_result = await _create_problem({"title": "P"})
    problem = json.loads(problem_result[0].text)

    solution_result = await _create_solution({"problem_id": problem["id"], "title": "S1"})
    solution = json.loads(solution_result[0].text)

    sub_problems = [
        {"title": "Auth", "description": "Auth service", "complexity": "medium"},
        {"title": "Database", "description": "DB", "complexity": "high", "parent_title": "Auth"},
    ]
    result = await _decompose_problem(
        {
            "problem_id": problem["id"],
            "solution_id": solution["id"],
            "sub_problems_json": json.dumps(sub_problems),
        }
    )
    data = json.loads(result[0].text)
    assert len(data) == 2
    assert data[0]["title"] == "Auth"


@pytest.mark.asyncio
async def test_role_cost_estimate(fresh_db):
    result = await _estimate_cost(
        {
            "provider": "role",
            "service": "solutions-architect",
            "region": "us",
            "parameters_json": json.dumps({"manual_rate": "180000"}),
        }
    )
    quote = json.loads(result[0].text)
    assert quote["provider"] == "role"
    assert quote["unit_price"] == "180000"


@pytest.mark.asyncio
async def test_attach_and_summarize_solution_cost(fresh_db):
    problem_result = await _create_problem({"title": "P"})
    problem = json.loads(problem_result[0].text)

    solution_result = await _create_solution({"problem_id": problem["id"], "title": "S1"})
    solution = json.loads(solution_result[0].text)

    await _attach_cost_to_solution(
        {
            "solution_id": solution["id"],
            "provider": "role",
            "service": "solutions-architect",
            "region": "us",
            "parameters_json": json.dumps({"manual_rate": "120000"}),
            "quantity": "1",
        }
    )

    summary_result = await _summarize_solution_cost({"solution_id": solution["id"]})
    summary = json.loads(summary_result[0].text)
    assert summary["currency"] == "USD"
    assert summary["total_monthly"] == "120000"
    assert summary["line_item_count"] == 1
