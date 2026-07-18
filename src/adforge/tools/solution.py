"""Solution MCP tools."""

from typing import Any

from mcp.types import TextContent, Tool

from adforge.models import Comment, Review, Solution
from adforge.models.common import Status
from adforge.persistence import SolutionRepository
from adforge.tools import registry


def _repo() -> SolutionRepository:
    return SolutionRepository()


async def _create_solution(arguments: dict[str, Any]) -> list[TextContent]:
    solution = _repo().save(
        Solution(
            problem_id=arguments["problem_id"],
            title=arguments["title"],
            body=arguments.get("body", ""),
        )
    )
    return [TextContent(type="text", text=solution.model_dump_json())]


async def _list_solutions(arguments: dict[str, Any]) -> list[TextContent]:
    solutions = _repo().list_for_problem(arguments["problem_id"])
    payload = [s.model_dump(mode="json") for s in solutions]
    return [TextContent(type="text", text=str(payload))]


async def _get_solution(arguments: dict[str, Any]) -> list[TextContent]:
    solution = _repo().get(arguments["solution_id"])
    if solution is None:
        return [TextContent(type="text", text=f"Solution not found: {arguments['solution_id']}")]
    return [TextContent(type="text", text=solution.model_dump_json())]


async def _update_solution_status(arguments: dict[str, Any]) -> list[TextContent]:
    solution = _repo().get(arguments["solution_id"])
    if solution is None:
        return [TextContent(type="text", text=f"Solution not found: {arguments['solution_id']}")]
    solution.status = Status(arguments["status"])
    solution = _repo().save(solution)
    return [TextContent(type="text", text=solution.model_dump_json())]


async def _add_solution_comment(arguments: dict[str, Any]) -> list[TextContent]:
    solution = _repo().get(arguments["solution_id"])
    if solution is None:
        return [TextContent(type="text", text=f"Solution not found: {arguments['solution_id']}")]
    solution.comments.append(Comment(author=arguments.get("author", ""), body=arguments["body"]))
    solution = _repo().save(solution)
    return [TextContent(type="text", text=solution.model_dump_json())]


async def _add_solution_review(arguments: dict[str, Any]) -> list[TextContent]:
    solution = _repo().get(arguments["solution_id"])
    if solution is None:
        return [TextContent(type="text", text=f"Solution not found: {arguments['solution_id']}")]
    solution.reviews.append(
        Review(
            author=arguments.get("author", ""),
            state=arguments.get("state", "commented"),
            body=arguments["body"],
        )
    )
    solution = _repo().save(solution)
    return [TextContent(type="text", text=solution.model_dump_json())]


registry.register(
    Tool(
        name="create_solution",
        description="Create a solution approach document for a problem.",
        inputSchema={
            "type": "object",
            "properties": {
                "problem_id": {"type": "string"},
                "title": {"type": "string"},
                "body": {"type": "string", "description": "Markdown body describing the approach"},
            },
            "required": ["problem_id", "title"],
        },
    ),
    _create_solution,
)

registry.register(
    Tool(
        name="list_solutions",
        description="List solution documents for a problem.",
        inputSchema={
            "type": "object",
            "properties": {"problem_id": {"type": "string"}},
            "required": ["problem_id"],
        },
    ),
    _list_solutions,
)

registry.register(
    Tool(
        name="get_solution",
        description="Get a solution document by ID.",
        inputSchema={
            "type": "object",
            "properties": {"solution_id": {"type": "string"}},
            "required": ["solution_id"],
        },
    ),
    _get_solution,
)

registry.register(
    Tool(
        name="update_solution_status",
        description="Update the status of a solution (draft, open, approved, rejected, closed).",
        inputSchema={
            "type": "object",
            "properties": {
                "solution_id": {"type": "string"},
                "status": {
                    "type": "string",
                    "enum": ["draft", "open", "in_progress", "approved", "rejected", "closed"],
                },
            },
            "required": ["solution_id", "status"],
        },
    ),
    _update_solution_status,
)

registry.register(
    Tool(
        name="add_solution_comment",
        description="Add a comment to a solution document.",
        inputSchema={
            "type": "object",
            "properties": {
                "solution_id": {"type": "string"},
                "author": {"type": "string"},
                "body": {"type": "string"},
            },
            "required": ["solution_id", "body"],
        },
    ),
    _add_solution_comment,
)

registry.register(
    Tool(
        name="add_solution_review",
        description="Add a review/approval record to a solution document.",
        inputSchema={
            "type": "object",
            "properties": {
                "solution_id": {"type": "string"},
                "author": {"type": "string"},
                "state": {"type": "string", "enum": ["commented", "approved", "changes_requested"]},
                "body": {"type": "string"},
            },
            "required": ["solution_id", "body"],
        },
    ),
    _add_solution_review,
)
