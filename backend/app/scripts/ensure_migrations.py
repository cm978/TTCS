from __future__ import annotations

import sys
from pathlib import Path

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url

from app.core.config import get_settings
from app.db.session import _connect_args

BACKEND_ROOT = Path(__file__).resolve().parents[2]
ALEMBIC_INI = BACKEND_ROOT / "alembic.ini"
ALEMBIC_DIR = BACKEND_ROOT / "alembic"
REMEDIATION_COMMAND = "cd backend && uv run alembic upgrade head"


class MigrationNotReadyError(RuntimeError):
    pass


def is_in_memory_sqlite(database_url: str) -> bool:
    url = make_url(database_url)
    return url.drivername.startswith("sqlite") and (url.database is None or url.database in {"", ":memory:"})


def _sqlite_database_exists(database_url: str) -> bool:
    url = make_url(database_url)
    if not url.drivername.startswith("sqlite") or is_in_memory_sqlite(database_url):
        return True

    database = url.database
    if database is None:
        return True

    return Path(database).exists()


def _alembic_config() -> Config:
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("script_location", str(ALEMBIC_DIR))
    return config


def _format_not_ready(current_heads: tuple[str, ...], expected_heads: tuple[str, ...]) -> str:
    current = ", ".join(current_heads) if current_heads else "none"
    expected = ", ".join(expected_heads) if expected_heads else "unknown"
    return (
        "Database schema is not at the latest Alembic revision. "
        f"Current revision: {current}; expected head: {expected}. "
        f"Run `{REMEDIATION_COMMAND}` before starting the backend."
    )


def ensure_database_at_head(database_url: str | None = None) -> bool:
    database_url = database_url or get_settings().database_url
    if is_in_memory_sqlite(database_url):
        return True

    config = _alembic_config()
    script = ScriptDirectory.from_config(config)
    expected_heads = tuple(sorted(script.get_heads()))

    if not _sqlite_database_exists(database_url):
        raise MigrationNotReadyError(_format_not_ready((), expected_heads))

    engine = create_engine(database_url, pool_pre_ping=True, connect_args=_connect_args(database_url))
    try:
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            current_heads = tuple(sorted(context.get_current_heads()))
    finally:
        engine.dispose()

    if current_heads != expected_heads:
        raise MigrationNotReadyError(_format_not_ready(current_heads, expected_heads))

    return True


def main() -> int:
    try:
        ensure_database_at_head()
    except MigrationNotReadyError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print("Database schema is at the latest Alembic revision.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
