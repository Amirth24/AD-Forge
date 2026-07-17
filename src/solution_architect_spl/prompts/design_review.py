"""Example prompt: design_review."""

from mcp.types import Prompt, PromptArgument

from solution_architect_spl.prompts import registry


async def _design_review_handler(arguments: dict | None) -> str:
    system = arguments.get("system", "the system") if arguments else "the system"
    return f"""Review the design of {system} against the following checklist:

- [ ] Does it have a single, well-defined responsibility?
- [ ] Are security controls layered (auth + validation + sanitization)?
- [ ] Is there a clear failure mode when dependencies are down?
- [ ] Are health checks and metrics in place?
- [ ] Can it be configured entirely via environment variables?

Provide a concise pass/fail for each item and one improvement recommendation.
"""


registry.register(
    Prompt(
        name="design_review",
        description="Run a design-review checklist against a system",
        arguments=[
            PromptArgument(
                name="system",
                description="Name of the system to review",
                required=False,
            ),
        ],
    ),
    _design_review_handler,
)
