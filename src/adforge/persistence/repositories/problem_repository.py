"""Problem repository."""

import sqlite3
from datetime import datetime

from adforge.models import Problem
from adforge.persistence.db import from_json_blob, get_connection, to_json_blob


class ProblemRepository:
    """CRUD for Problem statements."""

    def __init__(self, conn: sqlite3.Connection | None = None) -> None:
        self._conn = conn or get_connection()
        self._own_conn = conn is None

    def save(self, problem: Problem) -> Problem:
        problem.touch()
        self._conn.execute(
            """
            INSERT INTO problems (id, title, description, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title = excluded.title,
                description = excluded.description,
                tags = excluded.tags,
                updated_at = excluded.updated_at
            """,
            (
                problem.id,
                problem.title,
                problem.description,
                to_json_blob(problem.tags),
                problem.created_at.isoformat(),
                problem.updated_at.isoformat(),
            ),
        )
        self._conn.commit()
        return problem

    def get(self, problem_id: str) -> Problem | None:
        row = self._conn.execute("SELECT * FROM problems WHERE id = ?", (problem_id,)).fetchone()
        if row is None:
            return None
        return self._row_to_problem(row)

    def list_all(self, limit: int = 100, offset: int = 0) -> list[Problem]:
        rows = self._conn.execute(
            "SELECT * FROM problems ORDER BY updated_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
        return [self._row_to_problem(row) for row in rows]

    def delete(self, problem_id: str) -> bool:
        cur = self._conn.execute("DELETE FROM problems WHERE id = ?", (problem_id,))
        self._conn.commit()
        return cur.rowcount > 0

    @staticmethod
    def _row_to_problem(row: sqlite3.Row) -> Problem:
        return Problem(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            tags=from_json_blob(row["tags"]) or [],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def __del__(self) -> None:
        if self._own_conn:
            self._conn.close()
