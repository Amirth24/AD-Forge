"""Resource registry and base definitions."""

from dataclasses import dataclass
from typing import Awaitable, Callable, TypeAlias

from mcp.types import Resource

ResourceHandler: TypeAlias = Callable[[str], Awaitable[str]]


@dataclass(frozen=True)
class RegisteredResource:
    resource: Resource
    handler: ResourceHandler


class ResourceRegistry:
    """Central registry for MCP resources."""

    def __init__(self) -> None:
        self._resources: dict[str, RegisteredResource] = {}

    def register(self, resource: Resource, handler: ResourceHandler) -> None:
        if resource.uri in self._resources:
            raise ValueError(f"Resource '{resource.uri}' is already registered")
        self._resources[resource.uri] = RegisteredResource(resource, handler)

    def list_resources(self) -> list[Resource]:
        return [rr.resource for rr in self._resources.values()]

    async def read_resource(self, uri: str) -> str:
        try:
            registered = self._resources[uri]
        except KeyError:
            raise ValueError(f"Unknown resource: {uri}") from None
        return await registered.handler(uri)


registry = ResourceRegistry()
