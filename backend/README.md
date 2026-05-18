# TTCS Backend

FastAPI backend for TTCS authentication, teams, projects, invitations, memberships, and the Phase 2 empty board foundation.

## Commands

```bash
uv sync --extra dev
uv run alembic upgrade head
uv run python -m app.scripts.seed_demo_user
uv run uvicorn app.main:app --reload
uv run pytest -q
```

Run migrations before starting the server. The backend checks the configured database at startup and fails fast if its Alembic revision is behind the migration head.

If startup reports a migration readiness failure, or a local database has symptoms such as `no such table: teams`, run:

```bash
cd backend && uv run alembic upgrade head
```

You can also check migration readiness directly:

```bash
uv run python -m app.scripts.ensure_migrations
```

API routes are served under `/api/v1`:

- `GET /api/v1/health`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- Team routes under `/api/v1/teams`
- Project and board routes under `/api/v1/projects`

Passwords are stored with bcrypt hashes. JWT settings come from environment variables in `.env.example`; no production secret is committed.
