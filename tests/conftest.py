"""Shared test fixtures."""

import os
from collections.abc import Generator
from pathlib import Path

import pytest

# Use a temp SQLite file for all tests so module-level DB access stays isolated.
TEST_DB_PATH = Path(__file__).with_name("test.db").resolve()
os.environ["ADFORGE_DB_PATH"] = str(TEST_DB_PATH)

# Run migrations before anything else touches repositories.
from adforge.persistence import migrate  # noqa: E402

migrate()


@pytest.fixture(scope="session", autouse=True)
def _cleanup_test_db() -> Generator[None]:
    """Remove the test database after the session."""
    yield
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest.fixture
def fresh_db() -> None:
    """Recreate a clean test database for a test."""
    from adforge.persistence import get_connection

    with get_connection() as conn:
        for table in [
            "cost_line_items",
            "pricing_cache",
            "solution_edges",
            "solution_nodes",
            "sub_problems",
            "solutions",
            "problems",
        ]:
            conn.execute(f"DELETE FROM {table}")
        conn.commit()
