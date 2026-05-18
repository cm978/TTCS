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

## Phase 3 Task Execution Smoke

Use this smoke path after running migrations and `uv run python -m app.scripts.seed_demo_user`.

1. Open `http://localhost:5173` and log in with the local demo user.
2. Open the seeded `Phase 3 Demo Project` project board, or create a team/project manually.
3. Click `创建任务` to create a real persisted task, then click the task card to open the drawer.
4. In the drawer, edit basic task fields or add a one-level subtask.
5. Use `记录工作日志` with `工作日期`, `工时`, `工作类型`, and `工作内容`.
6. Check `是否阻塞`, enter a `阻塞原因` of at least 10 characters, and submit the log.
7. Confirm the board task card shows `阻塞中` and does not show the work-log body text.
8. Resolve the blocker with a note of at least 10 characters.
9. Open `/tasks/:taskId` from `打开完整详情` and confirm work-log history and blocker history are visible.

Phase 3 intentionally does not implement acceptance approve/reject Review controls, notification center, reports, real Git synchronization, or AI review. Those are later-phase capabilities.

## Verification

```bash
cd backend && uv run pytest -q
cd frontend && npm run typecheck && npm run test:unit -- --run && npm run build
```
