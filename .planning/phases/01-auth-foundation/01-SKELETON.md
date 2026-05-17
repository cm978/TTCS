# Walking Skeleton — TTCS

**Phase:** 1  
**Generated:** 2026-05-17

## Capability Proven End-to-End

A user can register, log in, refresh the browser to recover the JWT session, view their current-user information in a protected TTCS app shell, and log out so protected routes become inaccessible.

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Frontend framework | Vue 3 + Vite + TypeScript | Matches `ARCH-01`, keeps local startup fast, and supports componentized app-shell growth |
| Frontend state/routing | Pinia + Vue Router + Axios | Matches `ARCH-01`; gives a clean auth store, protected routes, and API client boundary |
| UI library | Ant Design Vue 4.x themed with TTCS tokens + `lucide-vue-next` | Speeds form/layout delivery while preserving project-specific visual quality from `01-UI-SPEC.md` |
| Backend framework | FastAPI + SQLAlchemy | Matches `ARCH-02`; supports typed REST endpoints and later service expansion |
| Data layer | MySQL 8 + Alembic migrations | Matches `ARCH-02`; creates durable migration discipline from the first table |
| Cache/realtime foundation | Redis 7 in Docker Compose, no Phase 1 notification logic | Matches `ARCH-02` and keeps later WebSocket/notification work unblocked without expanding Phase 1 |
| API style | RESTful JSON under `/api/v1` | Matches `ARCH-03`; creates stable route prefix for later modules |
| Auth | JWT bearer token, bcrypt password hashing, token stored in `localStorage` for MVP | Satisfies `AUTH-01..04`; localStorage keeps demo/dev flow simple and supports refresh recovery; risk is documented for later hardening |
| Backend shape | Single FastAPI monolith | Matches `ARCH-04`; avoids premature microservices |
| Directory layout | Root `backend/` and `frontend/` directories | Matches context and LLD; later phases can extend without moving Phase 1 code |
| Deployment target | Local dev environment with documented full-stack commands | CI/CD and hosted deployment are out of current MVP scope |

## Stack Touched in Phase 1

- [ ] Project scaffold: backend Python project, frontend Vite project, build/test commands.
- [ ] Routing: `/api/v1/health`, auth endpoints, frontend public/protected routes.
- [ ] Database: one real write through registration and one real read through `/me`.
- [ ] UI: login/register forms and protected `AppLayout` wired to the API.
- [ ] Local runtime: `docker-compose.yml` plus documented backend/frontend startup commands.

## Out of Scope (Deferred to Later Slices)

- Email verification.
- Password reset.
- Refresh tokens, multi-device sessions, session revocation.
- Teams, projects, tasks, work logs, task acceptance, evidence, notifications, reports.
- Real Git platform synchronization.
- AI/Agent review.
- Hosted CI/CD deployment.
- Microservice split.

## Subsequent Slice Plan

Each later phase adds one vertical slice on top of this skeleton without altering its architectural decisions:

- Phase 2: teams, projects, membership, and default board columns.
- Phase 3: task execution, work logs, blockers, and legal task status movement.
- Phase 4: evidence-gated task acceptance and human review.
- Phase 5: personal workbench, notifications, and project reporting.
- Phase 6: MVP validation, quality hardening, and demo readiness.

