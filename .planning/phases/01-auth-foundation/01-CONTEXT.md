# Phase 1: 应用基础与认证骨架 - Context

**Gathered:** 2026-05-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 1 delivers the runnable TTCS application foundation and the smallest useful authentication loop. It must establish the `backend/` + `frontend/` project structure, FastAPI/Vue startup path, database migration foundation, Docker-based local services, JWT-authenticated access, and a protected frontend shell.

This phase does not implement teams, projects, tasks, work logs, acceptance gates, dashboards, reports, real Git integration, or AI/Agent review. Those belong to later phases.

</domain>

<decisions>
## Implementation Decisions

### 认证页面与接口边界

- **D-01:** Phase 1 authentication is the minimal closed loop: register, login, get current user (`/me`), logout, and protected route access.
- **D-02:** Do not implement real email verification in Phase 1.
- **D-03:** Do not implement password reset or password reset placeholder pages in Phase 1.
- **D-04:** The authentication UI should stay focused on registration, login, protected access, current-user display, and logout.

### JWT 会话策略

- **D-05:** Phase 1 must prove that a logged-in user can access protected pages, refresh the browser and recover the session, and log out so protected pages are no longer accessible.
- **D-06:** Do not implement refresh tokens, multi-device session management, or advanced session revocation in Phase 1.
- **D-07:** Token storage strategy is delegated to planning/implementation. The planner should choose between `localStorage` and `httpOnly` cookie based on implementation complexity, FastAPI/Vue local development ergonomics, and security tradeoffs.
- **D-08:** Unless the planner identifies a better local-demo value, use the SRS token lifetime default of 24 hours.
- **D-09:** The plan must explicitly state the token storage choice and rationale.

### 工程脚手架形态

- **D-10:** Use the LLD-aligned dual-directory structure: `backend/` and `frontend/`.
- **D-11:** Backend foundation uses FastAPI + SQLAlchemy.
- **D-12:** Frontend foundation uses Vue 3 + Vite + TypeScript.
- **D-13:** Introduce Alembic in Phase 1 so database migrations exist from the start.
- **D-14:** Provide `docker-compose.yml` for local MySQL 8 and Redis 7 services.
- **D-15:** Provide environment variable examples such as `.env.example` for database URL, Redis URL, JWT secret, CORS, and related local settings.
- **D-16:** Startup commands should be clear for backend, frontend, and local infrastructure. Prefer an obvious sequence such as `docker compose up -d`, then backend startup from `backend/`, then frontend startup from `frontend/`.

### 开发与演示数据

- **D-17:** Provide a repeatable seed script or command to create one demo user for local development and course/demo review.
- **D-18:** Phase 1 seed data must only create a user. Do not seed teams, projects, tasks, work logs, or acceptance records.
- **D-19:** Demo credentials must be local/dev-only and must not be embedded as production secrets.
- **D-20:** Tests should use independent fixtures and must not depend on the development seed database.

### 前端首屏形态

- **D-21:** After login, users should land in a basic TTCS `AppLayout`, not a blank protected page.
- **D-22:** The layout should include a reusable shell suitable for later phases, such as top navigation, sidebar/navigation area, user menu/current-user affordance, and logout access.
- **D-23:** The content area should remain Phase 1 scoped: show a protected home placeholder or foundation page, not a real personal workspace.
- **D-24:** Do not implement Phase 5 workspace queues or dashboard metrics in Phase 1.

### UI/UX Pro Max 设计规范

- **D-25:** Frontend design must follow `ui-ux-pro-max` skill principles, especially accessibility, interaction feedback, performance, responsive layout, semantic color, form feedback, and navigation clarity.
- **D-26:** Use `design-system/MASTER.md` as the project-level visual source of truth for Phase 1 frontend work.
- **D-27:** The frontend should feel more visually polished than a default admin template: use a modern operational SaaS cockpit style with refined surfaces, semantic status accents, clear hierarchy, and purposeful motion.
- **D-28:** Do not use emoji as structural icons. Use a consistent vector icon family such as `lucide-vue-next` if icons are needed.
- **D-29:** Do not use decorative gradient orbs, bokeh blobs, fake dashboard data, or marketing-style hero composition in the app shell.
- **D-30:** Ant Design Vue may be used for speed and consistency, but components should be themed/wrapped with TTCS tokens so the UI does not look like an unstyled Ant Design default.
- **D-31:** Phase 1 auth screens should feel branded and product-specific, but must not imply teams/projects/tasks are implemented.
- **D-32:** Every auth form must include visible labels, inline errors, loading/disabled submit states, accessible focus states, and keyboard-friendly controls.

### the agent's Discretion

- Token storage is intentionally left to the planner/implementation phase, with the requirement that the choice be explained.
- Exact command names, package manager choice, and backend/frontend test tooling may be selected by the planner as long as they preserve the locked stack and local startup clarity.
- Fine visual details such as exact spacing tokens, icon choices, and auth page composition may be selected by the planner/implementation as long as they follow `design-system/MASTER.md` and do not expand Phase 1 scope.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### GSD Planning Baseline

- `.planning/PROJECT.md` — Project value, v1 boundaries, deferred scope, and locked MVP framing.
- `.planning/REQUIREMENTS.md` — Phase 1 requirements `AUTH-01..04` and `ARCH-01..04`, plus cross-phase boundaries.
- `.planning/ROADMAP.md` — Phase 1 goal, success criteria, and explicit non-goals.
- `.planning/STATE.md` — Current project state and workflow settings.
- `.planning/config.json` — GSD workflow configuration.
- `design-system/MASTER.md` — TTCS frontend visual system derived from `ui-ux-pro-max`; MUST read before frontend planning or implementation.
- `/Users/moon/.codex/skills/ui-ux-pro-max/SKILL.md` — UI/UX Pro Max source guidance.
- `/Users/moon/.codex/skills/ui-ux-pro-max/scripts/search.py` — UI/UX Pro Max search script. Verified available on 2026-05-17 after repair; useful for future design validation.

### Source Requirements and Design

- `01-requirements/02-srs.md` — SRS V2.4; authentication, stack, runtime environment, and phase-scope source.
- `02-design/02-high-level-design.md` — Architecture, module boundaries, deployment shape, API groups, and phase tradeoffs.
- `02-design/03-low-level-design.md` — Expected `backend/` and `frontend/` structures, auth-related service/API patterns, enums, and implementation detail baseline.
- `02-design/01-task-acceptance-design.md` — Not directly implemented in Phase 1, but defines the product's later evidence-gated completion model; do not design Phase 1 in a way that blocks it.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- None yet. The repository currently contains requirements/design/planning documents, not application source code.
- `design-system/MASTER.md` is a reusable project design asset for frontend planning and implementation.

### Established Patterns

- Planning documents establish `backend/` and `frontend/` as the expected source layout.
- The architecture is frontend/backend split with FastAPI, Vue 3, MySQL, Redis, REST `/api/v1`, JWT, and WebSocket capability reserved for later notifications.
- Phase structure is vertical MVP slicing; Phase 1 should create foundations that later phases extend without implementing their business features early.
- UI standards now prioritize accessibility, visible form labels, semantic tokens, consistent vector icons, meaningful loading/error states, 44px touch targets, and responsive app-shell layout.

### Integration Points

- New backend code should connect to future modules through an `/api/v1` route structure.
- New frontend code should establish router guards and a reusable `AppLayout` shell that later team/project/task views can occupy.
- Alembic migrations should become the foundation for later user, team, project, task, and acceptance tables.

</code_context>

<specifics>
## Specific Ideas

- The login/register flow should feel like a real TTCS app, not a throwaway test page.
- The protected post-login page should demonstrate that authentication and layout are working, while avoiding Phase 5 dashboard/workspace functionality.
- Seed data is for one demo user only; later business demo data belongs to later phases.
- The visual direction should be polished operational SaaS, with refined panels, status accents, and purposeful motion rather than plain scaffold pages.

</specifics>

<deferred>
## Deferred Ideas

- Email verification — future authentication enhancement, not Phase 1.
- Password reset — future authentication enhancement, not Phase 1.
- Refresh tokens and multi-device session management — future hardening, not Phase 1.
- Team/project/task demo seed data — belongs to later phases after those models exist.
- Real personal workspace queues and dashboard metrics — Phase 5.

</deferred>

---

*Phase: 1-应用基础与认证骨架*
*Context gathered: 2026-05-17*
