---
phase: 2
slug: team-project-board
status: complete
created: 2026-05-17
---

# Phase 2 — Pattern Map

## Source-of-Truth Patterns

| Area | Pattern Source | Implementation Guidance |
|---|---|---|
| Backend models | `backend/app/models/user.py` | Use typed SQLAlchemy `Mapped[...]`, integer primary keys, indexes, and timestamp columns |
| Backend schemas | `backend/app/schemas/auth.py` | Use Pydantic v2 models; public response schemas use `ConfigDict(from_attributes=True)` |
| Backend services | `backend/app/services/auth_service.py` | Put business rules and commits in service classes; raise explicit domain errors |
| Backend routers | `backend/app/api/v1/auth.py`, `backend/app/api/v1/router.py` | Use FastAPI routers under `/api/v1`, dependencies for DB/current user, and router inclusion by module |
| Auth dependency | `backend/app/deps.py` | Reuse `get_current_user`; add permission helpers instead of checking roles inline in every route |
| Migrations | `backend/alembic/env.py`, `backend/alembic/versions/20260517_0001_create_users.py` | Import models into metadata path and create explicit Alembic migration for Phase 2 tables |
| Backend tests | `backend/tests/conftest.py`, `backend/tests/test_auth.py` | Use in-memory SQLite fixtures, `Base.metadata.create_all`, and API-level assertions |
| Frontend API | `frontend/src/api/client.ts`, `frontend/src/api/auth.ts` | Use shared Axios client and typed API modules |
| Frontend stores | `frontend/src/stores/auth.ts` | Use Pinia state/actions with loading/error/hydration flags |
| Frontend routes | `frontend/src/router/index.ts` | Use protected routes and route names; `/app` currently points to `FoundationHomeView` and should be replaced |
| App shell | `frontend/src/layouts/AppLayout.vue` | Extend existing shell for team/project navigation and current-user context |
| UI tokens | `frontend/src/styles/tokens.css`, `design-system/MASTER.md` | Prefer semantic tokens, 44px targets, focus states, responsive layout, and no fake later-phase data |

## Files to Create or Modify

### Backend

- `backend/app/models/team.py` — `Team`, `TeamMember`, `TeamInvitation`, team enums.
- `backend/app/models/project.py` — `Project`, `ProjectMember`, `BoardColumn`, project/board enums.
- `backend/app/models/__init__.py` — export new model classes.
- `backend/alembic/env.py` — import new models for metadata.
- `backend/alembic/versions/*_create_team_project_board.py` — Phase 2 schema migration.
- `backend/app/schemas/team.py` — team, member, invitation schemas.
- `backend/app/schemas/project.py` — project, project member, board schemas.
- `backend/app/services/permissions.py` — team/project membership and role helpers.
- `backend/app/services/team_service.py` — team creation, invitations, membership.
- `backend/app/services/project_service.py` — project creation, project members, board retrieval.
- `backend/app/api/v1/teams.py` — team endpoints.
- `backend/app/api/v1/projects.py` — project endpoints.
- `backend/app/api/v1/router.py` — include team and project routers.
- `backend/tests/test_team_project.py` — backend invariants and API coverage.

### Frontend

- `frontend/src/types/team.ts` — team/member/invitation types.
- `frontend/src/types/project.ts` — project/member/board types.
- `frontend/src/api/teams.ts` — team API calls.
- `frontend/src/api/projects.ts` — project API calls.
- `frontend/src/stores/team.ts` — team list, invitations, member operations.
- `frontend/src/stores/project.ts` — project list, board, project member operations.
- `frontend/src/views/TeamProjectStartView.vue` — `/app` start/selection view.
- `frontend/src/views/TeamMembersView.vue` — team member management table.
- `frontend/src/views/ProjectBoardView.vue` — real empty board workspace.
- `frontend/src/components/team/CreateTeamModal.vue` — team creation.
- `frontend/src/components/team/InviteMemberModal.vue` — invitation form.
- `frontend/src/components/team/TeamMemberTable.vue` — team members and invitation table.
- `frontend/src/components/project/CreateProjectModal.vue` — project creation.
- `frontend/src/components/project/ProjectMemberDrawer.vue` — project member management.
- `frontend/src/components/project/BoardColumn.vue` — empty persisted board column display.
- `frontend/src/router/index.ts` — Phase 2 routes.
- `frontend/src/layouts/AppLayout.vue` — navigation update.
- `frontend/src/styles/tokens.css` — add any missing semantic state/shell tokens.
- `frontend/src/views/team-project.spec.ts` — route/UI tests.

## Data Flow

1. Current user loads through the existing auth store.
2. `/app` loads teams, projects, and invitations for the current user's email.
3. Creating a team creates `teams` and creator `team_members` rows.
4. Inviting a member creates `team_invitations`; accepting creates `team_members` and updates invitation status.
5. Creating a project creates `projects`, creator `project_members`, and five `board_columns` in one transaction.
6. Project board reads project metadata, member summary, and persisted columns.
7. Project member drawer mutates `project_members`, limited to existing team members.

## Patterns To Avoid

- Fake task cards, task counts, work-log prompts, acceptance buttons, report widgets, or notification feeds.
- Project members that are not team members.
- Team admin automatically receiving project edit/review authority.
- Role checks scattered directly across route handlers.
- MySQL-only constraints that break the existing SQLite test harness.
- Raw hex values scattered in Vue component styles.
