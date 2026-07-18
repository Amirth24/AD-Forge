"""DAG representation of a solution approach."""

from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class NodeType(StrEnum):
    """Kind of node in a solution DAG."""

    SUB_PROBLEM = "sub_problem"
    DECISION = "decision"
    DELIVERABLE = "deliverable"
    RISK = "risk"


class EdgeType(StrEnum):
    """Kind of edge in a solution DAG."""

    DEPENDS_ON = "depends_on"
    ALTERNATIVE_TO = "alternative_to"
    PRODUCES = "produces"
    BLOCKS = "blocks"


class SolutionNode(BaseModel):
    """A node in a solution approach DAG."""

    id: str = Field(default_factory=lambda: uuid4().hex)
    solution_id: str
    sub_problem_id: str | None = None
    node_type: NodeType = NodeType.SUB_PROBLEM
    title: str = ""
    description: str = ""
    data: dict[str, Any] = Field(default_factory=dict)


class SolutionEdge(BaseModel):
    """A directed edge between two nodes in a solution approach DAG."""

    id: str = Field(default_factory=lambda: uuid4().hex)
    solution_id: str
    from_node_id: str
    to_node_id: str
    edge_type: EdgeType = EdgeType.DEPENDS_ON
    data: dict[str, Any] = Field(default_factory=dict)
