"""Problem decomposition prompt."""

from typing import Any

from mcp.types import Prompt, PromptArgument

from adforge.prompts import registry


async def _problem_decomposition_handler(arguments: dict[str, Any] | None) -> str:
    problem = (arguments or {}).get("problem", "the system")
    return (
        "You are a senior solution architect. Break down the following problem"
        " into sub-problems that can be solved independently and then integrated.\n\n"
        f"Problem: {problem}\n\n"
        "For each sub-problem provide:\n"
        "1. Title (concise)\n"
        "2. Description (what must this sub-problem solve?)\n"
        "3. Tags (comma-separated, useful for narrowing focus)\n"
        "4. Complexity estimate: low, medium, high, or extreme\n"
        "5. Parent sub-problem (if any — use exact title of another sub-problem in this list)\n\n"
        "After listing sub-problems, suggest a sequential dependency graph between them"
        " and identify the riskiest item. Return the result as structured data suitable"
        " for the `decompose_problem` tool.\n"
    )


registry.register(
    Prompt(
        name="problem_decomposition",
        description="Break a problem statement into sub-problems and dependencies",
        arguments=[
            PromptArgument(
                name="problem",
                description="The problem statement to decompose",
                required=True,
            ),
        ],
    ),
    _problem_decomposition_handler,
)
