---
phase: 02-team-project-board
plan: 02
subsystem: api
tags: [fastapi, pydantic, rbac, teams, projects, board]
requires:
  - phase: 02-team-project-board
    provides: Plan 01 collaboration models and services
provides:
  - Protected team and invitation REST endpoints
  - Protected project, project member, and board REST endpoints
  - API tests for Phase 2 collaboration authority boundaries
affects: [frontend-api-clients, frontend-stores, phase-03-tasks]
tech-stack:
  added: []
  patterns: [Pydantic v2 response contracts, service-error-to-HTTP translation, protected FastAPI routers]
key-files:
  created:
    - backend/app/schemas/team.py
    - backend/app/schemas/project.py
    - backend/app/api/v1/teams.py
    - backend/app/api/v1/projects.py
  modified:
    - backend/app/api/v1/router.py
    - backend/tests/test_team_project.py
key-decisions:
  - "Project routes are included at /api/v1 so the same router can expose nested team project creation and top-level project resources."
  - "Board responses read persisted board_columns records rather than hard-coding frontend-only status columns."
  - "Team and project route handlers delegate authority checks to services and only translate domain errors to HTTP."
patterns-established:
  - "Routers keep current-user dependencies at every protected endpoint."
  - "API public member rows assemble UserPublic instead of exposing ORM internals."
requirements-completed: [TEAM-01, TEAM-02, TEAM-03, PROJ-01, PROJ-02, PROJ-03]
duration: 6 min
completed: 2026-05-17
---

# Phase 2 Plan 02: Team Project API Surface Summary

**Protected FastAPI collaboration endpoints for teams, invitations, projects, project members, and persisted board columns**

## Performance

- **Duration:** 6 min
- **Started:** 2026-05-17T15:02:35Z
- **Completed:** 2026-05-17T15:08:31Z
- **Tasks:** 4
- **Files modified:** 6

## Accomplishments

- Added team and invitation schemas with Phase 2 role/status contracts.
- Added project, member, board, and fixed status schemas with date validation.
- Added `/api/v1/teams` endpoints for team creation, membership, invitations, invite discovery, acceptance, and cancellation.
- Added `/api/v1/teams/{team_id}/projects` and `/api/v1/projects/*` endpoints for project creation, board retrieval, and member management.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add team and invitation schemas** - `72ae79b` (feat)
2. **Task 2: Add project, member, and board schemas** - `daa8eff` (feat)
3. **Task 3: Add protected team API routes** - `06c702c` (feat)
4. **Task 4: Add protected project and board API routes** - `c39b9aa` (feat)

**Plan metadata:** pending current commit

## Files Created/Modified

- `backend/app/schemas/team.py` - Public team, member, invitation, and role-update schemas.
- `backend/app/schemas/project.py` - Public project, member, board, and role-update schemas.
- `backend/app/api/v1/teams.py` - Protected team and invitation endpoints.
- `backend/app/api/v1/projects.py` - Protected project, board, and project-member endpoints.
- `backend/app/api/v1/router.py` - Router registration for Phase 2 APIs.
- `backend/tests/test_team_project.py` - API coverage for auth, invitations, boards, and role boundaries.

## Decisions Made

Project creation is exposed as the nested route `/api/v1/teams/{team_id}/projects`, while project board and member operations are top-level `/api/v1/projects/*` resources. This keeps creation anchored to team membership and keeps board links direct.

## Deviations from Plan

None - plan executed as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Ready for frontend data clients, Pinia stores, protected routes, and the `/app` team/project start view.

---
*Phase: 02-team-project-board*
*Completed: 2026-05-17*
