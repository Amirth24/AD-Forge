"""Problem MCP tools."""

from typing import Any

from mcp.types import TextContent, Tool

from adforge.models import Problem
from adforge.persistence import ProblemRepository, migrate
from adforge.tools import registry

# Ensure schema is ready before any repository access.
migrate()


def _repo() -> ProblemRepository:
    return ProblemRepository()


async def _create_problem(arguments: dict[str, Any]) -> list[TextContent]:
    title = arguments["title"]
    description = arguments.get("description", "")
    tags_csv = arguments.get("tags_csv", "")
    tags = [t.strip() for t in tags_csv.split(",") if t.strip()]
    problem = _repo().save(Problem(title=title, description=description, tags=tags))
    return [TextContent(type="text", text=problem.model_dump_json())]


async def _list_problems(arguments: dict[str, Any]) -> list[TextContent]:
    problems = _repo().list_all()
    payload = [p.model_dump(mode="json") for p in problems]
    return [TextContent(type="text", text=str(payload))]


async def _get_problem(arguments: dict[str, Any]) -> list[TextContent]:
    problem_id = arguments["problem_id"]
    problem = _repo().get(problem_id)
    if problem is None:
        return [TextContent(type="text", text=f"Problem not found: {problem_id}")]
    return [TextContent(type="text", text=problem.model_dump_json())]


async def _delete_problem(arguments: dict[str, Any]) -> list[TextContent]:
    problem_id = arguments["problem_id"]
    deleted = _repo().delete(problem_id)
    return [TextContent(type="text", text=f"Deleted: {deleted}")]


registry.register(
    Tool(
        name="create_problem",
        description="Create a new problem statement with optional tags.",
        inputSchema={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Short problem title"},
                "description": {"type": "string", "description": "Detailed problem description"},
                "tags_csv": {
                    "type": "string",
                    "description": "Comma-separated tags for the LLM to narrow focus",
                },
            },
            "required": ["title"],
        },
    ),
    _create_problem,
)

registry.register(
    Tool(
        name="list_problems",
        description="List all stored problem statements.",
        inputSchema={"type": "object", "properties": {}},
    ),
    _list_problems,
)

registry.register(
    Tool(
        name="get_problem",
        description="Get a problem statement by ID.",
        inputSchema={
            "type": "object",
            "properties": {"problem_id": {"type": "string"}},
            "required": ["problem_id"],
        },
    ),
    _get_problem,
)

registry.register(
    Tool(
        name="delete_problem",
        description="Delete a problem and its dependent solutions.",
        inputSchema={
            "type": "object",
            "properties": {"problem_id": {"type": "string"}},
            "required": ["problem_id"],
        },
    ),
    _delete_problem,
)
