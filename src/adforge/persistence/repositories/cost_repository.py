"""Cost line item repository and pricing cache."""

import hashlib
import json
import sqlite3
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from adforge.models import CostLineItem
from adforge.persistence.db import from_json_blob, get_connection, to_json_blob


class CostRepository:
    """CRUD for cost line items."""

    def __init__(self, conn: sqlite3.Connection | None = None) -> None:
        self._conn = conn or get_connection()
        self._own_conn = conn is None

    def save(self, item: CostLineItem) -> CostLineItem:
        self._conn.execute(
            """
            INSERT INTO cost_line_items (
                id, solution_id, sub_problem_id, provider, service, region,
                parameters, unit_price, quantity, unit, source_url, source_fetched_at, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                solution_id = excluded.solution_id,
                sub_problem_id = excluded.sub_problem_id,
                provider = excluded.provider,
                service = excluded.service,
                region = excluded.region,
                parameters = excluded.parameters,
                unit_price = excluded.unit_price,
                quantity = excluded.quantity,
                unit = excluded.unit,
                source_url = excluded.source_url,
                source_fetched_at = excluded.source_fetched_at
            """,
            (
                item.id,
                item.solution_id,
                item.sub_problem_id,
                item.provider,
                item.service,
                item.region,
                to_json_blob(item.parameters),
                str(item.unit_price),
                str(item.quantity),
                item.unit,
                item.source_url,
                item.source_fetched_at.isoformat(),
                item.created_at.isoformat(),
            ),
        )
        self._conn.commit()
        return item

    def list_for_solution(self, solution_id: str) -> list[CostLineItem]:
        rows = self._conn.execute(
            "SELECT * FROM cost_line_items WHERE solution_id = ? ORDER BY created_at",
            (solution_id,),
        ).fetchall()
        return [self._row_to_item(row) for row in rows]

    def delete(self, item_id: str) -> bool:
        cur = self._conn.execute("DELETE FROM cost_line_items WHERE id = ?", (item_id,))
        self._conn.commit()
        return cur.rowcount > 0

    @staticmethod
    def _row_to_item(row: sqlite3.Row) -> CostLineItem:
        return CostLineItem(
            id=row["id"],
            solution_id=row["solution_id"],
            sub_problem_id=row["sub_problem_id"],
            provider=row["provider"],
            service=row["service"],
            region=row["region"],
            parameters=from_json_blob(row["parameters"]) or {},
            unit_price=Decimal(row["unit_price"]),
            quantity=Decimal(row["quantity"]),
            unit=row["unit"],
            source_url=row["source_url"],
            source_fetched_at=datetime.fromisoformat(row["source_fetched_at"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def __del__(self) -> None:
        if self._own_conn:
            self._conn.close()


class PricingCache:
    """SQLite-backed TTL cache for provider pricing responses."""

    def __init__(self, conn: sqlite3.Connection | None = None, ttl_seconds: int = 86400) -> None:
        self._conn = conn or get_connection()
        self._own_conn = conn is None
        self._ttl_seconds = ttl_seconds

    def _make_key(
        self, provider: str, service: str, region: str, parameters: dict[str, Any]
    ) -> str:
        payload = json.dumps(
            {"provider": provider, "service": service, "region": region, "params": parameters},
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode()).hexdigest()

    def get(
        self, provider: str, service: str, region: str, parameters: dict[str, Any]
    ) -> dict[str, Any] | None:
        key = self._make_key(provider, service, region, parameters)
        now = datetime.now(UTC).isoformat()
        row = self._conn.execute(
            "SELECT response FROM pricing_cache WHERE key = ? AND expires_at > ?",
            (key, now),
        ).fetchone()
        if row is None:
            return None
        response = from_json_blob(row["response"])
        if response is None:
            return None
        return response  # type: ignore[no-any-return]

    def set(
        self,
        provider: str,
        service: str,
        region: str,
        parameters: dict[str, Any],
        response: dict[str, Any],
    ) -> None:
        key = self._make_key(provider, service, region, parameters)
        now = datetime.now(UTC)
        expires = now + timedelta(seconds=self._ttl_seconds)
        params_hash = key[:16]
        self._conn.execute(
            """
            INSERT INTO pricing_cache (
                key, provider, service, region, parameters_hash, response, fetched_at, expires_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                response = excluded.response,
                fetched_at = excluded.fetched_at,
                expires_at = excluded.expires_at
            """,
            (
                key,
                provider,
                service,
                region,
                params_hash,
                to_json_blob(response),
                now.isoformat(),
                expires.isoformat(),
            ),
        )
        self._conn.commit()

    def clear_expired(self) -> None:
        now = datetime.now(UTC).isoformat()
        self._conn.execute("DELETE FROM pricing_cache WHERE expires_at <= ?", (now,))
        self._conn.commit()

    def __del__(self) -> None:
        if self._own_conn:
            self._conn.close()
