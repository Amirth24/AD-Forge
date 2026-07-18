"""Prompt registry and base definitions."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from mcp.types import Prompt

type PromptHandler = Callable[[dict[str, Any] | None], Awaitable[str]]


@dataclass(frozen=True)
class RegisteredPrompt:
    prompt: Prompt
    handler: PromptHandler


class PromptRegistry:
    """Central registry for MCP prompts."""

    def __init__(self) -> None:
        self._prompts: dict[str, RegisteredPrompt] = {}

    def register(self, prompt: Prompt, handler: PromptHandler) -> None:
        if prompt.name in self._prompts:
            raise ValueError(f"Prompt '{prompt.name}' is already registered")
        self._prompts[prompt.name] = RegisteredPrompt(prompt, handler)

    def list_prompts(self) -> list[Prompt]:
        return [rp.prompt for rp in self._prompts.values()]

    async def get_prompt(self, name: str, arguments: dict[str, Any] | None = None) -> str:
        try:
            registered = self._prompts[name]
        except KeyError:
            raise ValueError(f"Unknown prompt: {name}") from None
        return await registered.handler(arguments)


registry = PromptRegistry()
