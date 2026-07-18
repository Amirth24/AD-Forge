"""Tests for server initialization."""

from adforge.prompts import registry as prompt_registry
from adforge.server import app
from adforge.tools import registry as tool_registry


def test_server_app_exists():
    assert app is not None
    assert app.name == "adforge"


def test_new_tools_registered():
    tools = tool_registry.list_tools()
    names = {t.name for t in tools}
    assert "create_problem" in names
    assert "create_solution" in names
    assert "decompose_problem" in names
    assert "estimate_cost" in names
    assert "attach_cost_to_solution" in names


def test_prompt_registered():
    prompts = prompt_registry.list_prompts()
    names = {p.name for p in prompts}
    assert "problem_decomposition" in names
