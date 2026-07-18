"""Problem decomposition and DAG tools."""

import json
from typing import Any

from mcp.types import TextContent, Tool

from adforge.models import Complexity, EdgeType, NodeType, SolutionNode, SubProblem
from adforge.models.common import Status
from adforge.persistence import (
    DagRepository,
    ProblemRepository,
    SubProblemRepository,
)
from adforge.tools import registry


def _problem_repo() -> ProblemRepository:
    return ProblemRepository()


def _sub_repo() -> SubProblemRepository:
    return SubProblemRepository()


def _dag_repo() -> DagRepository:
    return DagRepository()


async def _decompose_problem(arguments: dict[str, Any]) -> list[TextContent]:
    """Create sub-problems for a problem and optionally link them to a solution.

    sub_problems_json is a JSON list of objects with keys:
        title, description, tags_csv, complexity (low/medium/high/extreme), parent_title
    """
    problem_id = arguments["problem_id"]
    solution_id = arguments.get("solution_id")
    if _problem_repo().get(problem_id) is None:
        return [TextContent(type="text", text=f"Problem not found: {problem_id}")]

    items = json.loads(arguments["sub_problems_json"])
    created: list[SubProblem] = []
    title_to_sub: dict[str, SubProblem] = {}

    for item in items:
        tags = [t.strip() for t in item.get("tags_csv", "").split(",") if t.strip()]
        sub = _sub_repo().save(
            SubProblem(
                problem_id=problem_id,
                solution_id=solution_id,
                title=item["title"],
                description=item.get("description", ""),
                tags=tags,
                complexity=Complexity[item.get("complexity", "medium").upper()],
                status=Status.DRAFT,
            )
        )
        created.append(sub)
        title_to_sub[sub.title] = sub

    # Wire parent/child relationships if requested.
    for item in items:
        parent_title = item.get("parent_title")
        if parent_title and parent_title in title_to_sub and item["title"] in title_to_sub:
            child = title_to_sub[item["title"]]
            parent = title_to_sub[parent_title]
            child.parent_id = parent.id
            _sub_repo().save(child)

    # Build a simple DAG if a solution_id is given: nodes for each sub-problem,
    # edges from earlier sub-problem to later (sequential dependency) by default.
    if solution_id:
        _dag_repo().delete_for_solution(solution_id)
        nodes: dict[str, SolutionNode] = {}
        for sub in created:
            node = _dag_repo().save_node(
                SolutionNode(
                    solution_id=solution_id,
                    sub_problem_id=sub.id,
                    node_type=NodeType.SUB_PROBLEM,
                    title=sub.title,
                    description=sub.description,
                )
            )
            nodes[sub.id] = node
        previous: SolutionNode | None = None
        for sub in created:
            node = nodes[sub.id]
            if previous is not None:
                from adforge.models import SolutionEdge

                _dag_repo().save_edge(
                    SolutionEdge(
                        solution_id=solution_id,
                        from_node_id=previous.id,
                        to_node_id=node.id,
                        edge_type=EdgeType.DEPENDS_ON,
                    )
                )
            previous = node

    payload = [s.model_dump(mode="json") for s in created]
    return [TextContent(type="text", text=json.dumps(payload))]


async def _get_solution_dag(arguments: dict[str, Any]) -> list[TextContent]:
    solution_id = arguments["solution_id"]
    nodes = _dag_repo().get_nodes(solution_id)
    edges = _dag_repo().get_edges(solution_id)
    payload = {
        "nodes": [n.model_dump(mode="json") for n in nodes],
        "edges": [e.model_dump(mode="json") for e in edges],
    }
    return [TextContent(type="text", text=json.dumps(payload))]


registry.register(
    Tool(
        name="decompose_problem",
        description="Break a problem into sub-problems and store a solution DAG.",
        inputSchema={
            "type": "object",
            "properties": {
                "problem_id": {"type": "string"},
                "solution_id": {
                    "type": "string",
                    "description": "Optional solution to attach sub-problems to",
                },
                "sub_problems_json": {
                    "type": "string",
                    "description": (
                        "JSON list of {title, description, tags_csv, complexity, parent_title}"
                    ),
                },
            },
            "required": ["problem_id", "sub_problems_json"],
        },
    ),
    _decompose_problem,
)

registry.register(
    Tool(
        name="get_solution_dag",
        description="Return the stored DAG nodes and edges for a solution.",
        inputSchema={
            "type": "object",
            "properties": {"solution_id": {"type": "string"}},
            "required": ["solution_id"],
        },
    ),
    _get_solution_dag,
)
