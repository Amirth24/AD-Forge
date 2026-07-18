"""SQLite connection and migration utilities."""

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

from adforge.utils.logging import get_logger

logger = get_logger(__name__)

DEFAULT_DB_NAME = "adforge.db"


def _db_path() -> Path:
    """Resolve the SQLite database path from env or project root."""
    env_path = os.environ.get("ADFORGE_DB_PATH")
    if env_path:
        return Path(env_path)

    # Fall back to project root, discovered from this file's location.
    project_root = Path(__file__).resolve().parents[4]
    return project_root / DEFAULT_DB_NAME


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with JSON-friendly row factory."""
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _load_migrations() -> list[tuple[int, str]]:
    """Load migration SQL files in order."""
    migrations_dir = Path(__file__).with_name("migrations")
    files = sorted(migrations_dir.glob("*.sql"))
    migrations = []
    for file in files:
        try:
            number = int(file.stem.split("_", 1)[0])
        except ValueError:
            logger.warning("Skipping migration file without numeric prefix", file=file.name)
            continue
        migrations.append((number, file.read_text()))
    migrations.sort(key=lambda x: x[0])
    return migrations


def migrate() -> None:
    """Run pending migrations."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS migrations (
                version INTEGER PRIMARY KEY
            )
            """
        )
        cur = conn.execute("SELECT version FROM migrations")
        applied = {row["version"] for row in cur.fetchall()}

        for version, sql in _load_migrations():
            if version in applied:
                continue
            logger.info("Applying migration", version=version)
            conn.executescript(sql)
            conn.execute("INSERT INTO migrations (version) VALUES (?)", (version,))
            conn.commit()


def to_json_blob(value: Any) -> str:
    """Serialize a value to a JSON string for SQLite storage."""
    return json.dumps(value, default=str)


def from_json_blob(text: str | None) -> Any:
    """Deserialize a JSON string from SQLite storage."""
    if text is None:
        return None
    return json.loads(text)
