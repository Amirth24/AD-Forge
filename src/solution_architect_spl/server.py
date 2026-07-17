"""Solution Architect MCP Server

An MCP server exposing tools, resources, and prompts for solution architecture tasks.
Designed to also ship with Hermes-compatible skills.
"""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
    Resource,
    Prompt,
    PromptArgument,
)

from solution_architect_spl.tools import registry as tool_registry
from solution_architect_spl.resources import registry as resource_registry
from solution_architect_spl.prompts import registry as prompt_registry
from solution_architect_spl.utils.logging import get_logger

# Import tool / resource / prompt modules so they self-register at import time
import solution_architect_spl.tools.hello  # noqa: F401
import solution_architect_spl.resources.principles  # noqa: F401
import solution_architect_spl.prompts.design_review  # noqa: F401

logger = get_logger(__name__)

# Create the MCP application
app = Server("solution-architect-spl")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Return all registered tools."""
    return tool_registry.list_tools()


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Dispatch to the appropriate tool handler."""
    return await tool_registry.call_tool(name, arguments)


@app.list_resources()
async def list_resources() -> list[Resource]:
    """Return all registered resources."""
    return resource_registry.list_resources()


@app.read_resource()
async def read_resource(uri: str) -> str:
    """Return resource content by URI."""
    return await resource_registry.read_resource(uri)


@app.list_prompts()
async def list_prompts() -> list[Prompt]:
    """Return all registered prompts."""
    return prompt_registry.list_prompts()


@app.get_prompt()
async def get_prompt(name: str, arguments: dict | None = None) -> str:
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
