"""Sub-problem repository."""

import sqlite3
from datetime import datetime

from adforge.models import Complexity, Status, SubProblem
from adforge.persistence.db import from_json_blob, get_connection, to_json_blob


class SubProblemRepository:
    """CRUD for sub-problems."""

    def __init__(self, conn: sqlite3.Connection | None = None) -> None:
        self._conn = conn or get_connection()
        self._own_conn = conn is None

    def save(self, sub_problem: SubProblem) -> SubProblem:
        sub_problem.touch()
        self._conn.execute(
            """
            INSERT INTO sub_problems (
                id, problem_id, solution_id, parent_id, title, description,
                tags, complexity, status, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                problem_id = excluded.problem_id,
                solution_id = excluded.solution_id,
                parent_id = excluded.parent_id,
                title = excluded.title,
                description = excluded.description,
                tags = excluded.tags,
                complexity = excluded.complexity,
                status = excluded.status,
                updated_at = excluded.updated_at
            """,
            (
                sub_problem.id,
                sub_problem.problem_id,
                sub_problem.solution_id,
                sub_problem.parent_id,
                sub_problem.title,
                sub_problem.description,
                to_json_blob(sub_problem.tags),
                sub_problem.complexity.value,
                sub_problem.status.value,
                sub_problem.created_at.isoformat(),
                sub_problem.updated_at.isoformat(),
            ),
        )
        self._conn.commit()
        return sub_problem

    def get(self, sub_problem_id: str) -> SubProblem | None:
        row = self._conn.execute(
            "SELECT * FROM sub_problems WHERE id = ?", (sub_problem_id,)
        ).fetchone()
        if row is None:
            return None
        return self._row_to_sub_problem(row)

    def list_for_problem(self, problem_id: str) -> list[SubProblem]:
        rows = self._conn.execute(
            "SELECT * FROM sub_problems WHERE problem_id = ? ORDER BY created_at",
            (problem_id,),
        ).fetchall()
        return [self._row_to_sub_problem(row) for row in rows]

    def list_for_solution(self, solution_id: str) -> list[SubProblem]:
        rows = self._conn.execute(
            "SELECT * FROM sub_problems WHERE solution_id = ? ORDER BY created_at",
            (solution_id,),
        ).fetchall()
        return [self._row_to_sub_problem(row) for row in rows]

    def delete(self, sub_problem_id: str) -> bool:
        cur = self._conn.execute("DELETE FROM sub_problems WHERE id = ?", (sub_problem_id,))
        self._conn.commit()
        return cur.rowcount > 0

    @staticmethod
    def _row_to_sub_problem(row: sqlite3.Row) -> SubProblem:
        return SubProblem(
            id=row["id"],
            problem_id=row["problem_id"],
            solution_id=row["solution_id"],
            parent_id=row["parent_id"],
            title=row["title"],
            description=row["description"],
            tags=from_json_blob(row["tags"]) or [],
            complexity=Complexity(row["complexity"]),
            status=Status(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def __del__(self) -> None:
        if self._own_conn:
            self._conn.close()
