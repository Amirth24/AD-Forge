"""Solution repository."""

import sqlite3
from datetime import datetime

from adforge.models import CostSummary, Solution
from adforge.models.common import Status
from adforge.persistence.db import from_json_blob, get_connection, to_json_blob


class SolutionRepository:
    """CRUD for Solution documents."""

    def __init__(self, conn: sqlite3.Connection | None = None) -> None:
        self._conn = conn or get_connection()
        self._own_conn = conn is None

    def save(self, solution: Solution) -> Solution:
        solution.touch()
        self._conn.execute(
            """
            INSERT INTO solutions (
                id, problem_id, title, status, body, comments, reviews,
                labels, assignees, cost_summary, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                problem_id = excluded.problem_id,
                title = excluded.title,
                status = excluded.status,
                body = excluded.body,
                comments = excluded.comments,
                reviews = excluded.reviews,
                labels = excluded.labels,
                assignees = excluded.assignees,
                cost_summary = excluded.cost_summary,
                updated_at = excluded.updated_at
            """,
            (
                solution.id,
                solution.problem_id,
                solution.title,
                solution.status.value,
                solution.body,
                to_json_blob([c.model_dump(mode="json") for c in solution.comments]),
                to_json_blob([r.model_dump(mode="json") for r in solution.reviews]),
                to_json_blob(solution.labels),
                to_json_blob(solution.assignees),
                to_json_blob(
                    solution.cost_summary.model_dump(mode="json") if solution.cost_summary else None
                ),
                solution.created_at.isoformat(),
                solution.updated_at.isoformat(),
            ),
        )
        self._conn.commit()
        return solution

    def get(self, solution_id: str) -> Solution | None:
        row = self._conn.execute("SELECT * FROM solutions WHERE id = ?", (solution_id,)).fetchone()
        if row is None:
            return None
        return self._row_to_solution(row)

    def list_for_problem(self, problem_id: str) -> list[Solution]:
        rows = self._conn.execute(
            "SELECT * FROM solutions WHERE problem_id = ? ORDER BY updated_at DESC",
            (problem_id,),
        ).fetchall()
        return [self._row_to_solution(row) for row in rows]

    def delete(self, solution_id: str) -> bool:
        cur = self._conn.execute("DELETE FROM solutions WHERE id = ?", (solution_id,))
        self._conn.commit()
        return cur.rowcount > 0

    @staticmethod
    def _row_to_solution(row: sqlite3.Row) -> Solution:
        cost_blob = from_json_blob(row["cost_summary"])
        cost_summary = CostSummary(**cost_blob) if cost_blob else None
        return Solution(
            id=row["id"],
            problem_id=row["problem_id"],
            title=row["title"],
            status=Status(row["status"]),
            body=row["body"],
            comments=from_json_blob(row["comments"]) or [],
            reviews=from_json_blob(row["reviews"]) or [],
            labels=from_json_blob(row["labels"]) or [],
            assignees=from_json_blob(row["assignees"]) or [],
            cost_summary=cost_summary,
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def __del__(self) -> None:
        if self._own_conn:
            self._conn.close()
