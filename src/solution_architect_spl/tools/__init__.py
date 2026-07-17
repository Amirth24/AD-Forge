"""Tool registry and base definitions."""

from dataclasses import dataclass
from typing import Awaitable, Callable, TypeAlias

from mcp.types import TextContent, Tool

ToolHandler: TypeAlias = Callable[[dict], Awaitable[list[TextContent]]]


@dataclass(frozen=True)
class RegisteredTool:
    tool: Tool
    handler: ToolHandler


class ToolRegistry:
    """Central registry for MCP tools."""

    def __init__(self) -> None:
        self._tools: dict[str, RegisteredTool] = {}

    def register(self, tool: Tool, handler: ToolHandler) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered")
        self._tools[tool.name] = RegisteredTool(tool, handler)

    def list_tools(self) -> list[Tool]:
        return [rt.tool for rt in self._tools.values()]

    async def call_tool(self, name: str, arguments: dict) -> list[TextContent]:
        try:
            registered = self._tools[name]
        except KeyError:
            raise ValueError(f"Unknown tool: {name}") from None
        return await registered.handler(arguments)


registry = ToolRegistry()
