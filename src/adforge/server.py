"""AD Forge MCP Server

An MCP server exposing tools, resources, and prompts for data-driven solution
architecture. Designed to also ship with Hermes-compatible skills.
"""

from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Prompt,
    Resource,
    TextContent,
    Tool,
)

import adforge.prompts.problem_decomposition  # noqa: F401
import adforge.tools.cost  # noqa: F401
import adforge.tools.decompose  # noqa: F401

# Import tool / resource / prompt modules so they self-register at import time
import adforge.tools.problem  # noqa: F401
import adforge.tools.solution  # noqa: F401
import adforge.tools.solution_cost  # noqa: F401
from adforge.prompts import registry as prompt_registry
from adforge.resources import registry as resource_registry
from adforge.tools import registry as tool_registry
from adforge.utils.logging import get_logger

logger = get_logger(__name__)

# Create the MCP application
app = Server("adforge")


@app.list_tools()  # type: ignore[no-untyped-call,untyped-decorator]
async def list_tools() -> list[Tool]:
    """Return all registered tools."""
    return tool_registry.list_tools()


@app.call_tool()  # type: ignore[untyped-decorator]
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Dispatch to the appropriate tool handler."""
    return await tool_registry.call_tool(name, arguments)


@app.list_resources()  # type: ignore[no-untyped-call,untyped-decorator]
async def list_resources() -> list[Resource]:
    """Return all registered resources."""
    return resource_registry.list_resources()


@app.read_resource()  # type: ignore[no-untyped-call,untyped-decorator]
async def read_resource(uri: str) -> str:
    """Return resource content by URI."""
    return await resource_registry.read_resource(uri)


@app.list_prompts()  # type: ignore[no-untyped-call,untyped-decorator]
async def list_prompts() -> list[Prompt]:
    """Return all registered prompts."""
    return prompt_registry.list_prompts()


@app.get_prompt()  # type: ignore[no-untyped-call,untyped-decorator]
async def get_prompt(name: str, arguments: dict[str, Any] | None = None) -> str:
    """Return prompt content by name."""
    return await prompt_registry.get_prompt(name, arguments)


async def main() -> None:
    """Run the MCP server over stdio."""
    logger.info("Starting Solution Architect MCP server")
    async with stdio_server() as (read, write):
        await app.run(
            read,
            write,
            app.create_initialization_options(),
        )


def run() -> None:
    """Synchronous entry point for the console script."""
    import asyncio

    asyncio.run(main())
