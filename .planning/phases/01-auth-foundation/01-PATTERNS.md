---
phase: 1
slug: auth-foundation
status: complete
created: 2026-05-17
---

# Phase 1 — Pattern Map

## Codebase State

No application source code exists yet. The repository currently contains requirements, design, and GSD planning artifacts. Phase 1 therefore establishes the first implementation patterns rather than adapting existing code modules.

## Source-of-Truth Patterns

| Area | Pattern Source | Implementation Guidance |
|---|---|---|
| Backend layout | `02-design/03-low-level-design.md` section 2.1 | Use `backend/app/api/v1`, `core`, `db`, `models`, `schemas`, `services`, and `tests` |
| Frontend layout | `02-design/03-low-level-design.md` section 2.2 | Use `frontend/src/api`, `layouts`, `router`, `stores`, `views`, and `types` |
| Phase boundary | `.planning/phases/01-auth-foundation/01-CONTEXT.md` | Build auth foundation only; no team/project/task/acceptance UI or API |
| UI system | `design-system/MASTER.md` and `01-UI-SPEC.md` | Use TTCS tokens, Ant Design Vue theming, visible labels, accessible focus, responsive app shell |
| Requirements mapping | `.planning/REQUIREMENTS.md` | Cover `AUTH-01..04` and `ARCH-01..04` only in Phase 1 |

## New Patterns Phase 1 Should Establish

- Backend route modules should expose `/api/v1/...` routers and delegate business logic to services.
- Database access should go through SQLAlchemy session dependencies; avoid global sessions.
- Models and schemas should be separate.
- Auth dependencies should be reusable by later phases for permission checks.
- Frontend API access should go through a single Axios client with token injection and `401` handling.
- Auth state should live in a Pinia store; route guards should depend on the store rather than page-local token checks.
- Layout and token styling should be reusable so later phases can add team/project/task screens without redesigning the shell.

## Patterns To Avoid

- Creating later-phase model files with empty placeholders.
- Hard-coding dev credentials as secrets.
- Building a frontend shell with fake dashboard metrics or task queues.
- Accepting default Ant Design styling without TTCS tokens.
- Adding multiple auth strategies in Phase 1.

