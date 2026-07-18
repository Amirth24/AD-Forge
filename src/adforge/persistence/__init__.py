"""Persistence layer: SQLite-backed storage for problems, solutions, and costs."""

from adforge.persistence.db import get_connection, migrate
from adforge.persistence.repositories.cost_repository import CostRepository
from adforge.persistence.repositories.dag_repository import DagRepository
from adforge.persistence.repositories.problem_repository import ProblemRepository
from adforge.persistence.repositories.solution_repository import SolutionRepository
from adforge.persistence.repositories.sub_problem_repository import (
    SubProblemRepository,
)

__all__ = [
    "get_connection",
    "migrate",
    "ProblemRepository",
    "SolutionRepository",
    "SubProblemRepository",
    "DagRepository",
    "CostRepository",
]
