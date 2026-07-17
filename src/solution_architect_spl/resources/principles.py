"""Example resource: static/architecture_principles.md."""

from mcp.types import Resource

from solution_architect_spl.resources import registry


async def _principles_handler(uri: str) -> str:
    return """# Architecture Principles

1. Single Responsibility — one purpose per server.
2. Defense in Depth — layered security controls.
3. Fail-Safe — graceful degradation under failure.
4. Observability — metrics, logs, and health checks everywhere.
"""


registry.register(
    Resource(
        uri="static://architecture/principles",
        name="Architecture Principles",
        description="Core principles for designing robust systems",
        mimeType="text/markdown",
    ),
    _principles_handler,
)
