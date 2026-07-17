"""Tests for server initialization."""

from solution_architect_spl.server import app
from solution_architect_spl.tools import registry as tool_registry
from solution_architect_spl.resources import registry as resource_registry
from solution_architect_spl.prompts import registry as prompt_registry


def test_server_app_exists():
    """The app should be a Server instance."""
    assert app is not None
    assert app.name == "solution-architect-spl"


def test_tools_registered():
    """At least the hello_world tool should be registered."""
    tools = tool_registry.list_tools()
    names = [t.name for t in tools]
    assert "hello_world" in names


def test_resources_registered():
    """At least the principles resource should be registered."""
    resources = resource_registry.list_resources()
    uris = [str(r.uri) for r in resources]
    assert "static://architecture/principles" in uris


def test_prompts_registered():
    """At least the design_review prompt should be registered."""
    prompts = prompt_registry.list_prompts()
    names = [p.name for p in prompts]
    assert "design_review" in names
