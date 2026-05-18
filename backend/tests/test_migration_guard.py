from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text

from app.core.config import get_settings
from app.main import create_app
from app.scripts.ensure_migrations import MigrationNotReadyError, _alembic_config, ensure_database_at_head, is_in_memory_sqlite


def sqlite_url(path: Path) -> str:
    return f"sqlite:///{path}"


def write_revision(database_path: Path, revision: str) -> str:
    database_url = sqlite_url(database_path)
    engine = create_engine(database_url)
    try:
        with engine.begin() as connection:
            connection.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)"))
            connection.execute(text("INSERT INTO alembic_version (version_num) VALUES (:revision)"), {"revision": revision})
    finally:
        engine.dispose()
    return database_url


def current_alembic_head() -> str:
    heads = ScriptDirectory.from_config(_alembic_config()).get_heads()
    assert len(heads) == 1
    return heads[0]


def test_migration_guard_rejects_stale_database(tmp_path):
    database_url = write_revision(tmp_path / "stale.db", "20260517_0001")

    with pytest.raises(MigrationNotReadyError) as exc:
        ensure_database_at_head(database_url)

    message = str(exc.value)
    assert "Current revision: 20260517_0001" in message
    assert f"expected head: {current_alembic_head()}" in message
    assert "cd backend && uv run alembic upgrade head" in message


def test_migration_guard_accepts_database_at_head(tmp_path):
    database_url = write_revision(tmp_path / "current.db", current_alembic_head())

    assert ensure_database_at_head(database_url) is True


def test_migration_guard_skips_in_memory_sqlite():
    assert is_in_memory_sqlite("sqlite:///:memory:") is True
    assert is_in_memory_sqlite("sqlite://") is True
    assert ensure_database_at_head("sqlite:///:memory:") is True


def test_app_startup_rejects_stale_database(tmp_path, monkeypatch):
    database_url = write_revision(tmp_path / "stale-startup.db", "20260517_0001")
    monkeypatch.setenv("DATABASE_URL", database_url)
    get_settings.cache_clear()

    try:
        with pytest.raises(MigrationNotReadyError) as exc:
            with TestClient(create_app()):
                pass
    finally:
        get_settings.cache_clear()

    assert "cd backend && uv run alembic upgrade head" in str(exc.value)
