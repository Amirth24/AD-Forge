"""Example tool: hello_world."""

from mcp.types import TextContent, Tool

from solution_architect_spl.tools import registry


async def _hello_handler(arguments: dict) -> list[TextContent]:
    name = arguments.get("name", "world")
    return [TextContent(type="text", text=f"Hello, {name}!")]


registry.register(
    Tool(
        name="hello_world",
        description="Say hello to someone",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name to greet",
                },
            },
        },
    ),
    _hello_handler,
)
