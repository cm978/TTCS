---
phase: 1
slug: auth-foundation
status: complete
created: 2026-05-17
requirements: [AUTH-01, AUTH-02, AUTH-03, AUTH-04, ARCH-01, ARCH-02, ARCH-03, ARCH-04]
---

# Phase 1 Research — 应用基础与认证骨架

## RESEARCH COMPLETE

Phase 1 should prove the full TTCS stack with the smallest useful auth loop: a user can register, log in, persist a browser session across refresh, call `/api/v1/auth/me`, see a protected TTCS app shell, and log out.

## Inputs Read

- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/phases/01-auth-foundation/01-CONTEXT.md`
- `.planning/phases/01-auth-foundation/01-UI-SPEC.md`
- `design-system/MASTER.md`
- `02-design/02-high-level-design.md`
- `02-design/03-low-level-design.md`
- `01-requirements/02-srs.md`

## Scope Boundary

In scope:

- `backend/` FastAPI app scaffold with `/api/v1` router.
- SQLAlchemy model/session foundation and Alembic migration.
- MySQL 8 and Redis 7 local services through `docker-compose.yml`.
- User registration, login, current-user, logout-compatible frontend behavior.
- JWT bearer access token with 24-hour expiry for the local/demo MVP.
- Vue 3 + Vite + TypeScript frontend with Pinia, Vue Router, Axios, Ant Design Vue, and `lucide-vue-next`.
- Reusable TTCS `AppLayout` shell and protected home page.
- One dev-only seed user command.
- Focused automated tests for auth and shell behavior.

Out of scope:

- Email verification, password reset, refresh tokens, multi-device sessions, session revocation.
- Teams, projects, tasks, work logs, acceptance gates, reports, dashboard queues, notifications implementation, Git integration, AI review.

## Recommended Technical Approach

### Backend Foundation

Use a package layout aligned to the LLD but only create Phase 1 files:

- `backend/app/main.py`
- `backend/app/api/v1/router.py`
- `backend/app/api/v1/auth.py`
- `backend/app/core/config.py`
- `backend/app/core/security.py`
- `backend/app/db/session.py`
- `backend/app/db/base.py`
- `backend/app/models/user.py`
- `backend/app/schemas/auth.py`
- `backend/app/services/auth_service.py`
- `backend/app/scripts/seed_demo_user.py`
- `backend/tests/`

Use FastAPI dependency injection for database sessions and current-user resolution. Keep auth logic in a service module so later permission and team/project logic can build on it without moving endpoint code.

### Database and Migrations

Use SQLAlchemy 2 style models and Alembic from the start. The initial migration should create only the `users` table:

- `id`
- `email`
- `hashed_password`
- `display_name`
- `is_active`
- `created_at`
- `updated_at`

The email column should be unique and indexed. The model should avoid team/project/task relationships until later phases create those tables.

### Password and JWT

Use bcrypt through Passlib or a maintained bcrypt wrapper. Plain passwords must never be logged or returned.

Use JWT bearer tokens with:

- `sub`: user id or stable user identifier.
- `email`: optional convenience claim if implementation keeps it non-sensitive.
- `exp`: 24 hours from issue time.
- Signing secret from environment, never hard-coded.
- Algorithm from environment or default `HS256`.

Token storage choice: use `localStorage` for Phase 1, with explicit documentation.

Rationale:

- SRS and design docs call for JWT bearer flow.
- Vue/Axios local development remains simple and visible for course/demo review.
- Browser refresh can recover the session, satisfying the Phase 1 context.
- `httpOnly` cookies would improve XSS resistance but introduce CORS credential, CSRF, and cookie-domain complexity that is better handled when session hardening becomes a later phase.

Risk controls:

- Token lifetime stays at 24 hours.
- Store only the JWT, not profile data or secrets.
- Clear token on logout and on `401`.
- Avoid rendering untrusted HTML.
- Document the future migration path to `httpOnly` cookie or refresh-token sessions.

### API Contract

All endpoints live under `/api/v1`.

Recommended endpoints:

- `GET /api/v1/health`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

Logout does not need a backend invalidation endpoint in Phase 1 because there is no server-side session store. The frontend clears the token and redirects to login. If an endpoint is added for UI symmetry, it should be a no-op documented as client-side logout.

### Frontend Foundation

Use Vue 3 + Vite + TypeScript with:

- Pinia `auth` store.
- Vue Router routes for login, register, protected home, and a redirect fallback.
- Axios API client with base URL from `VITE_API_BASE_URL`.
- Request interceptor injecting `Authorization: Bearer <token>`.
- Response interceptor clearing local auth state on `401`.
- Ant Design Vue themed through TTCS CSS variables/tokens.
- `lucide-vue-next` for icons where useful.

The protected view must use `AppLayout` and show a Phase 1 foundation page with current user information from `/me`. It must not show fake team/project/task/dashboard data.

### Local Runtime

Create root `docker-compose.yml` with:

- `mysql:8`
- `redis:7`
- persistent named volumes.
- local ports suitable for development.

Create `.env.example` files for backend/frontend or a root example with clearly separated sections:

- database URL
- Redis URL
- JWT secret
- JWT expiry minutes
- CORS origins
- API base URL

### Testing Strategy

Backend:

- `pytest`
- FastAPI `TestClient` or `httpx`
- test database fixture independent from dev seed data
- tests for register/login/me/password hash/token rejection

Frontend:

- `vitest`
- Vue Test Utils
- route guard/store tests
- auth view form validation smoke tests

End-to-end smoke:

- Document manual local verification commands.
- Add Playwright only if setup cost is low; otherwise defer full browser E2E to later stabilization and keep Phase 1 with focused unit/integration tests plus manual smoke.

## Validation Architecture

Use fast automated checks after each task and a full suite at wave boundaries.

Backend quick command:

```bash
cd backend && pytest -q
```

Frontend quick command:

```bash
cd frontend && npm run test:unit -- --run
```

Full phase command:

```bash
cd backend && pytest -q && cd ../frontend && npm run typecheck && npm run test:unit -- --run && npm run build
```

Manual smoke remains required because Phase 1 proves local multi-process behavior:

1. `docker compose up -d`
2. Start backend.
3. Start frontend.
4. Register a user.
5. Refresh protected page and confirm `/me` still works.
6. Log out and confirm protected route redirects to login.

## Key Risks

| Risk | Mitigation |
|---|---|
| Auth scope expands into password reset/email verification | Keep endpoints and UI limited to register/login/me/logout |
| LocalStorage token XSS risk | Document MVP tradeoff, keep token short-lived, clear on logout/401, avoid unsafe HTML |
| Alembic introduced late or inconsistently | Create migration foundation in the first implementation plan |
| UI looks like raw Ant Design default | Use `design-system/MASTER.md` tokens and `01-UI-SPEC.md` contracts from the first frontend task |
| Seed data leaks into tests | Keep seed script dev-only and tests fixture-owned |

## Research Decision

Proceed with a four-plan Phase 1:

1. Walking skeleton scaffold and local runtime.
2. Auth backend vertical slice.
3. Auth frontend vertical slice.
4. Integration hardening, documentation, and full-stack smoke.

