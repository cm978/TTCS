# TTCS

TTCS is a demo-first task collaboration MVP. Phase 1 provides the runnable foundation: FastAPI backend, Vue frontend, local MySQL/Redis services, and the minimal authentication loop.

## Local Startup

1. Copy local configuration:

   ```bash
   cp .env.example .env
   ```

2. Start infrastructure:

   ```bash
   docker compose up -d
   ```

3. Install and run the backend:

   ```bash
   cd backend
   uv sync --extra dev
   uv run alembic upgrade head
   uv run python -m app.scripts.seed_demo_user
   uv run uvicorn app.main:app --reload
   ```

4. Install and run the frontend:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Phase 1 Auth Smoke

1. Open `http://localhost:5173`.
2. Create an account or use the local demo seed credentials from `.env`.
3. Log in and confirm the protected TTCS shell appears.
4. Refresh the browser and confirm the session recovers through `/api/v1/auth/me`.
5. Use `退出登录` and confirm `/app` redirects back to login.

Phase 1 uses a JWT Bearer token stored in `localStorage` for local/demo ergonomics and browser-refresh recovery. This is intentionally documented as an MVP tradeoff; later hardening can migrate to `httpOnly` cookie or refresh-token sessions.

Phase 1 does not implement teams, projects, tasks, work logs, acceptance gates, workspace queues, reports, Git synchronization, or AI review.

## Verification

```bash
cd backend && uv run pytest -q
cd frontend && npm run typecheck && npm run test:unit -- --run && npm run build
```

