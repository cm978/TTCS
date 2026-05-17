# TTCS Backend

FastAPI backend for Phase 1 authentication foundation.

## Commands

```bash
uv sync --extra dev
uv run alembic upgrade head
uv run python -m app.scripts.seed_demo_user
uv run uvicorn app.main:app --reload
uv run pytest -q
```

API routes are served under `/api/v1`:

- `GET /api/v1/health`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

Passwords are stored with bcrypt hashes. JWT settings come from environment variables in `.env.example`; no production secret is committed.

