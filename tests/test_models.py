"""Tests for core Pydantic models."""

from decimal import Decimal

from adforge.models import Complexity, CostLineItem, Problem, SubProblem


def test_problem_defaults():
    p = Problem(title="Build an API")
    assert p.id
    assert p.tags == []
    assert p.description == ""


def test_sub_problem_complexity():
    sp = SubProblem(problem_id="p1", title="Auth", complexity=Complexity.HIGH)
    assert sp.complexity == Complexity.HIGH


def test_cost_line_item_total():
    item = CostLineItem(
        solution_id="s1",
        provider="aws",
        service="EC2",
        region="us-east-1",
        unit_price=Decimal("0.10"),
        quantity=Decimal("730"),
    )
    assert item.total == Decimal("73.00")
