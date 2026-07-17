"""Unit tests for tool registry."""

import pytest

from solution_architect_spl.tools import ToolRegistry
from solution_architect_spl.tools.hello import registry as hello_registry


@pytest.mark.asyncio
async def test_hello_tool():
    """The hello_world tool should greet by name."""
    tools = hello_registry.list_tools()
    names = [t.name for t in tools]
    assert "hello_world" in names

    result = await hello_registry.call_tool("hello_world", {"name": "Alice"})
    assert len(result) == 1
    assert result[0].text == "Hello, Alice!"


@pytest.mark.asyncio
async def test_hello_tool_default():
    """The hello_world tool should default to 'world' when no name given."""
    result = await hello_registry.call_tool("hello_world", {})
    assert result[0].text == "Hello, world!"
