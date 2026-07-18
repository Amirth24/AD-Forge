"""Solution DAG repository."""

import sqlite3

from adforge.models import EdgeType, NodeType, SolutionEdge, SolutionNode
from adforge.persistence.db import from_json_blob, get_connection, to_json_blob


class DagRepository:
    """CRUD for solution approach DAGs."""

    def __init__(self, conn: sqlite3.Connection | None = None) -> None:
        self._conn = conn or get_connection()
        self._own_conn = conn is None

    def save_node(self, node: SolutionNode) -> SolutionNode:
        self._conn.execute(
            """
            INSERT INTO solution_nodes (
                id, solution_id, sub_problem_id, node_type, title, description, data
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                solution_id = excluded.solution_id,
                sub_problem_id = excluded.sub_problem_id,
                node_type = excluded.node_type,
                title = excluded.title,
                description = excluded.description,
                data = excluded.data
            """,
            (
                node.id,
                node.solution_id,
                node.sub_problem_id,
                node.node_type.value,
                node.title,
                node.description,
                to_json_blob(node.data),
            ),
        )
        self._conn.commit()
        return node

    def save_edge(self, edge: SolutionEdge) -> SolutionEdge:
        self._conn.execute(
            """
            INSERT INTO solution_edges (id, solution_id, from_node_id, to_node_id, edge_type, data)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                solution_id = excluded.solution_id,
                from_node_id = excluded.from_node_id,
                to_node_id = excluded.to_node_id,
                edge_type = excluded.edge_type,
                data = excluded.data
            """,
            (
                edge.id,
                edge.solution_id,
                edge.from_node_id,
                edge.to_node_id,
                edge.edge_type.value,
                to_json_blob(edge.data),
            ),
        )
        self._conn.commit()
        return edge

    def get_nodes(self, solution_id: str) -> list[SolutionNode]:
        rows = self._conn.execute(
            "SELECT * FROM solution_nodes WHERE solution_id = ?", (solution_id,)
        ).fetchall()
        return [self._row_to_node(row) for row in rows]

    def get_edges(self, solution_id: str) -> list[SolutionEdge]:
        rows = self._conn.execute(
            "SELECT * FROM solution_edges WHERE solution_id = ?", (solution_id,)
        ).fetchall()
        return [self._row_to_edge(row) for row in rows]

    def delete_for_solution(self, solution_id: str) -> None:
        self._conn.execute("DELETE FROM solution_edges WHERE solution_id = ?", (solution_id,))
        self._conn.execute("DELETE FROM solution_nodes WHERE solution_id = ?", (solution_id,))
        self._conn.commit()

    @staticmethod
    def _row_to_node(row: sqlite3.Row) -> SolutionNode:
        return SolutionNode(
            id=row["id"],
            solution_id=row["solution_id"],
            sub_problem_id=row["sub_problem_id"],
            node_type=NodeType(row["node_type"]),
            title=row["title"],
            description=row["description"],
            data=from_json_blob(row["data"]) or {},
        )

    @staticmethod
    def _row_to_edge(row: sqlite3.Row) -> SolutionEdge:
        return SolutionEdge(
            id=row["id"],
            solution_id=row["solution_id"],
            from_node_id=row["from_node_id"],
            to_node_id=row["to_node_id"],
            edge_type=EdgeType(row["edge_type"]),
            data=from_json_blob(row["data"]) or {},
        )

    def __del__(self) -> None:
        if self._own_conn:
            self._conn.close()
