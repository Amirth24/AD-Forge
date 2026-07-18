"""Tests for SQLite repositories."""

import pytest

from adforge.models import Complexity, Problem, Solution, Status, SubProblem
from adforge.persistence import (
    CostRepository,
    DagRepository,
    ProblemRepository,
    SolutionRepository,
    SubProblemRepository,
)


@pytest.mark.asyncio
async def test_problem_repository_crud(fresh_db):
    repo = ProblemRepository()
    problem = repo.save(Problem(title="Test Problem", description="Desc", tags=["api", "aws"]))
    fetched = repo.get(problem.id)
    assert fetched is not None
    assert fetched.title == "Test Problem"
    assert fetched.tags == ["api", "aws"]

    problems = repo.list_all()
    assert any(p.id == problem.id for p in problems)

    assert repo.delete(problem.id) is True
    assert repo.get(problem.id) is None


@pytest.mark.asyncio
async def test_solution_repository_links_to_problem(fresh_db):
    problem_repo = ProblemRepository()
    solution_repo = SolutionRepository()
    problem = problem_repo.save(Problem(title="P"))
    solution = solution_repo.save(Solution(problem_id=problem.id, title="S1"))

    fetched = solution_repo.get(solution.id)
    assert fetched is not None
    assert fetched.problem_id == problem.id
    assert fetched.status == Status.DRAFT

    solutions = solution_repo.list_for_problem(problem.id)
    assert len(solutions) == 1


@pytest.mark.asyncio
async def test_sub_problem_repository(fresh_db):
    problem_repo = ProblemRepository()
    problem = problem_repo.save(Problem(title="P"))
    repo = SubProblemRepository()
    sub = repo.save(SubProblem(problem_id=problem.id, title="Auth", complexity=Complexity.MEDIUM))
    assert repo.get(sub.id) is not None
    assert repo.list_for_problem(problem.id)[0].title == "Auth"


@pytest.mark.asyncio
async def test_dag_repository(fresh_db):
    problem_repo = ProblemRepository()
    solution_repo = SolutionRepository()
    dag_repo = DagRepository()
    problem = problem_repo.save(Problem(title="P"))
    solution = solution_repo.save(Solution(problem_id=problem.id, title="S"))

    from adforge.models import EdgeType, NodeType, SolutionEdge, SolutionNode

    n1 = dag_repo.save_node(
        SolutionNode(solution_id=solution.id, node_type=NodeType.SUB_PROBLEM, title="A")
    )
    n2 = dag_repo.save_node(
        SolutionNode(solution_id=solution.id, node_type=NodeType.SUB_PROBLEM, title="B")
    )
    dag_repo.save_edge(
        SolutionEdge(
            solution_id=solution.id,
            from_node_id=n1.id,
            to_node_id=n2.id,
            edge_type=EdgeType.DEPENDS_ON,
        )
    )

    nodes = dag_repo.get_nodes(solution.id)
    edges = dag_repo.get_edges(solution.id)
    assert len(nodes) == 2
    assert len(edges) == 1
    assert edges[0].from_node_id == n1.id


@pytest.mark.asyncio
async def test_cost_repository(fresh_db):
    problem_repo = ProblemRepository()
    solution_repo = SolutionRepository()
    cost_repo = CostRepository()
    problem = problem_repo.save(Problem(title="P"))
    solution = solution_repo.save(Solution(problem_id=problem.id, title="S"))

    from decimal import Decimal

    from adforge.models import CostLineItem

    cost_repo.save(
        CostLineItem(
            solution_id=solution.id,
            provider="aws",
            service="EC2",
            region="us-east-1",
            unit_price=Decimal("0.05"),
            quantity=Decimal("730"),
        )
    )
    items = cost_repo.list_for_solution(solution.id)
    assert len(items) == 1
    assert items[0].total == Decimal("36.50")
