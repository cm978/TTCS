---
phase: 02-team-project-board
plan: 01
subsystem: backend
tags: [fastapi, sqlalchemy, alembic, rbac, teams, projects]
requires:
  - phase: 01-auth-foundation
    provides: authenticated User model and current-user dependency
provides:
  - Team, invitation, project, project membership, and board-column persistence
  - Shared permission helpers for team/project role checks
  - Domain services enforcing Phase 2 collaboration invariants
affects: [phase-03-tasks, phase-04-acceptance, backend-api, frontend-stores]
tech-stack:
  added: []
  patterns: [SQLAlchemy typed models, service-level RBAC invariants, per-task pytest coverage]
key-files:
  created:
    - backend/app/models/team.py
    - backend/app/models/project.py
    - backend/alembic/versions/20260517_0002_create_team_project_board.py
    - backend/app/services/permissions.py
    - backend/app/services/team_service.py
    - backend/app/services/project_service.py
    - backend/tests/test_team_project.py
  modified:
    - backend/app/models/__init__.py
    - backend/alembic/env.py
    - backend/tests/conftest.py
key-decisions:
  - "Invitation uniqueness for active pending records is enforced in service logic for SQLite/MySQL portability."
  - "Team administrators can view team projects through can_view_team_project but cannot manage project members without PROJECT_MANAGER."
  - "Removing a team member also removes their project memberships inside that team to preserve the team-member-only project invariant."
patterns-established:
  - "Permission helpers return membership records and raise stable domain errors for API translation."
  - "Project creation writes project, creator manager membership, and five persisted board columns in one transaction."
requirements-completed: [TEAM-01, TEAM-02, TEAM-03, PROJ-01, PROJ-02, PROJ-03]
duration: 18 min
completed: 2026-05-17
---

# Phase 2 Plan 01: Team Project Domain Foundation Summary

**SQLAlchemy collaboration domain with teams, invitations, projects, project roles, fixed board columns, and service-enforced RBAC invariants**

## Performance

- **Duration:** 18 min
- **Started:** 2026-05-17T14:44:00Z
- **Completed:** 2026-05-17T15:02:35Z
- **Tasks:** 3
- **Files modified:** 10

## Accomplishments

- Added Phase 2 persistence for teams, team members, invitations, projects, project members, and board columns.
- Added Alembic migration for only the six Phase 2 collaboration tables.
- Added domain services and permission helpers for invitations, team/project role boundaries, and last-admin/last-manager protection.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add team, project, invitation, and board models** - `0e64a17` (feat)
2. **Task 2: Add migration for Phase 2 collaboration tables** - `a2f3dc4` (feat)
3. **Task 3: Add permission helpers and domain services** - `ef6b70b` (feat)

**Plan metadata:** pending current commit

## Files Created/Modified

- `backend/app/models/team.py` - Team, membership, invitation roles, and invitation statuses.
- `backend/app/models/project.py` - Project membership and fixed board-column status model.
- `backend/alembic/versions/20260517_0002_create_team_project_board.py` - Phase 2 collaboration schema.
- `backend/app/services/permissions.py` - Shared team/project permission checks.
- `backend/app/services/team_service.py` - Team creation, invitation, role, and removal operations.
- `backend/app/services/project_service.py` - Project creation, board access, and project member operations.
- `backend/tests/test_team_project.py` - Service-level coverage for collaboration invariants.

## Decisions Made

Invitation uniqueness is enforced in service logic rather than a partial unique index so the same behavior works in the SQLite test suite and the configured relational target.

Team admins receive project visibility but not project-member management authority. Project membership edits require `PROJECT_MANAGER`, preserving the role boundary needed by later task and acceptance phases.

## Deviations from Plan

None - plan executed as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Ready for Plan 02 API work. The backend now has stable services and domain errors for routers to translate into protected `/api/v1` responses.

---
*Phase: 02-team-project-board*
*Completed: 2026-05-17*
