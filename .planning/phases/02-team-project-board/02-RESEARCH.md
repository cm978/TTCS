---
phase: 2
slug: team-project-board
status: complete
created: 2026-05-17
---

# Phase 2 — Research: 团队、项目与基础看板

## Research Goal

Plan Phase 2 so execution can safely extend the Phase 1 auth foundation into real team/project collaboration without leaking Phase 3 task behavior or Phase 5 workspace/reporting behavior into this phase.

Phase 2 must cover `TEAM-01`, `TEAM-02`, `TEAM-03`, `PROJ-01`, `PROJ-02`, and `PROJ-03`.

## Current Codebase Baseline

### Backend

- Existing backend layout already follows the LLD shape: `backend/app/api/v1`, `core`, `db`, `models`, `schemas`, `services`, and `tests`.
- `backend/app/models/user.py` establishes the SQLAlchemy model style: typed `Mapped[...]` columns, integer primary keys, indexed fields, and `created_at` / `updated_at` timestamps.
- `backend/app/schemas/auth.py` establishes Pydantic v2 response schemas with `ConfigDict(from_attributes=True)`.
- `backend/app/services/auth_service.py` establishes service classes that own business logic and transaction commits.
- `backend/app/api/v1/auth.py` establishes router functions that depend on `get_db` and `get_current_user`, convert domain errors into `HTTPException`, and return schema-backed response models.
- `backend/alembic/env.py` currently imports `User` directly so Alembic metadata sees the auth model. Phase 2 must update model imports so new tables are visible to migrations.
- Backend tests use in-memory SQLite with `Base.metadata.create_all` in `backend/tests/conftest.py`, so Phase 2 models and relationships must work under SQLite as well as the configured MySQL target.

### Frontend

- Existing frontend layout follows the Phase 1 implementation: `frontend/src/api`, `layouts`, `router`, `stores`, `types`, `views`, and shared token styles.
- `frontend/src/api/client.ts` centralizes Axios base URL, Bearer token injection, and `401` handling.
- `frontend/src/stores/auth.ts` establishes the Pinia store pattern: state, getters, action methods, loading/error flags, and persistence through localStorage where needed.
- `frontend/src/router/index.ts` establishes protected route guards and redirects unauthenticated users to login.
- `frontend/src/layouts/AppLayout.vue` is the protected app shell that Phase 2 should evolve for team/project navigation.
- `frontend/src/styles/tokens.css` already defines semantic color and radius tokens, but some component-local raw colors remain in Phase 1 shell styles. Phase 2 frontend work should prefer tokens and can add tokens where the design system needs additional shell/sidebar states.

## Source Requirements and Design Findings

### Team Management

The SRS defines:

- Team name length: 2-50 characters.
- Team name uniqueness: global uniqueness in SRS.
- Team description max length: 500 characters.
- Each user can create at most 5 teams.
- Team invitations expire after 7 days.
- Same user/email can have at most one pending invitation at a time for the same relevant context.
- Invitation roles are administrator/member.
- Teams must always retain at least one administrator.

The Phase 2 context refines this:

- No real email is sent in Phase 2.
- Invitations can target unregistered emails.
- Pending invitations are matched by email after registration/login.
- Invitation states are `PENDING`, `ACCEPTED`, `EXPIRED`, and `CANCELLED`.
- A team administrator can cancel pending invitations.
- At most one active pending invitation exists for the same team/email pair.

### Project Management and Board

The SRS defines:

- Project name length: 2-100 characters.
- Project description max length: 1000 characters.
- End date must be later than start date.
- Team members can create projects.
- Project creator becomes project manager.
- Project members are selected from team members.
- New projects have default columns: 待办, 进行中, 待验收, 打回修改, 已完成.

The Phase 2 context refines this:

- Phase 2 project roles are only `PROJECT_MANAGER` and `PROJECT_MEMBER`.
- Detailed project roles are deferred.
- Board column customization is out of scope.
- Default columns are persisted as `board_columns`.
- Default columns map to task statuses `TODO`, `IN_PROGRESS`, `IN_REVIEW`, `REJECTED`, and `DONE`.
- Project creation should transactionally create the project, initial project manager membership, and default board columns.

### Permission Boundary

The HLD says the system uses RBAC plus resource ownership checks. It also states team roles and project roles are separate, task operation permissions are primarily based on project membership, and project managers own review authority later.

Phase 2 must lock the boundary now:

- Team administrators may view projects under the team.
- Team administrators do not automatically gain project edit authority.
- Project member and role management requires `PROJECT_MANAGER` authority.
- Project members must already be team members.
- Team and project minimum-authority constraints must be backend-enforced.

## Recommended Backend Shape

### Models and Enums

Create Phase 2 models using existing SQLAlchemy style:

- `backend/app/models/team.py`
  - `Team`
  - `TeamMember`
  - `TeamInvitation`
  - `TeamRole`
  - `TeamInvitationStatus`
- `backend/app/models/project.py`
  - `Project`
  - `ProjectMember`
  - `BoardColumn`
  - `ProjectRole`
  - `BoardColumnStatus`

Use string enums for externally visible role/status values:

- `TEAM_ADMIN`
- `TEAM_MEMBER`
- `PROJECT_MANAGER`
- `PROJECT_MEMBER`
- `PENDING`
- `ACCEPTED`
- `EXPIRED`
- `CANCELLED`
- `TODO`
- `IN_PROGRESS`
- `IN_REVIEW`
- `REJECTED`
- `DONE`

Planner should decide exact SQLAlchemy enum storage style, but execution should keep response values stable as the strings above.

### Database Constraints

Recommended constraints and indexes:

- `teams.name` unique, indexed.
- `team_members` unique on `(team_id, user_id)`.
- `team_invitations` indexed by `(team_id, email)` and `(email, status)`.
- Enforce at most one active pending invitation per `team_id + normalized email` in service logic; if the chosen database supports a partial unique index, use it only if it remains portable enough for tests.
- `projects` indexed by `team_id`.
- `project_members` unique on `(project_id, user_id)`.
- `board_columns` unique on `(project_id, status)` and `(project_id, position)`.

SQLite test compatibility matters. If MySQL-specific partial indexes would complicate the in-memory test suite, enforce active-invitation uniqueness in service logic plus broad database indexes rather than relying only on database-specific constraints.

### Services

Use service classes with explicit domain errors, following `AuthService`:

- `TeamService`
  - `create_team(actor, payload)`
  - `list_my_teams(actor)`
  - `list_team_members(actor, team_id)`
  - `invite_member(actor, team_id, payload)`
  - `list_team_invitations(actor, team_id)`
  - `accept_invitation(actor, invitation_id)`
  - `cancel_invitation(actor, invitation_id)`
  - `update_member_role(actor, team_id, user_id, role)`
  - `remove_member(actor, team_id, user_id)`
- `ProjectService`
  - `create_project(actor, team_id, payload)`
  - `list_accessible_projects(actor, team_id optional)`
  - `get_project_board(actor, project_id)`
  - `list_project_members(actor, project_id)`
  - `add_project_member(actor, project_id, team_member_user_id, role)`
  - `update_project_member_role(actor, project_id, user_id, role)`
  - `remove_project_member(actor, project_id, user_id)`

Use transactional service boundaries for:

- Team creation + initial `TEAM_ADMIN`.
- Invitation acceptance + team membership creation + invitation status update.
- Project creation + initial `PROJECT_MANAGER` + five board columns.
- Role/removal operations that must verify minimum administrator/manager counts.

### Permission Helpers

Add a small permission/service layer now rather than scattering checks in routers:

- `ensure_team_member(actor_id, team_id)`
- `ensure_team_admin(actor_id, team_id)`
- `ensure_project_member(actor_id, project_id)`
- `ensure_project_manager(actor_id, project_id)`
- `can_view_team_project(actor_id, project_id)` for project member OR team admin visibility.

These helpers are the foundation for Phase 3 tasks and Phase 4 review permissions. They should return role/membership records where useful to avoid duplicate queries.

### API Shape

Recommended endpoints:

- `POST /api/v1/teams`
- `GET /api/v1/teams`
- `GET /api/v1/teams/{team_id}`
- `GET /api/v1/teams/{team_id}/members`
- `PATCH /api/v1/teams/{team_id}/members/{user_id}`
- `DELETE /api/v1/teams/{team_id}/members/{user_id}`
- `POST /api/v1/teams/{team_id}/invitations`
- `GET /api/v1/teams/{team_id}/invitations`
- `POST /api/v1/teams/invitations/{invitation_id}/accept`
- `POST /api/v1/teams/invitations/{invitation_id}/cancel`
- `GET /api/v1/teams/my-invitations`
- `POST /api/v1/teams/{team_id}/projects`
- `GET /api/v1/projects`
- `GET /api/v1/projects/{project_id}/board`
- `GET /api/v1/projects/{project_id}/members`
- `POST /api/v1/projects/{project_id}/members`
- `PATCH /api/v1/projects/{project_id}/members/{user_id}`
- `DELETE /api/v1/projects/{project_id}/members/{user_id}`

The planner may adjust exact route names, but the plan must preserve discoverability of pending invitations for the current user's email and direct navigation from project creation to board.

### Error Handling

Existing API returns simple `detail` strings. Phase 2 can continue that pattern for consistency, but should use stable domain error classes so a later error-code envelope can be introduced cleanly.

Important error cases:

- Duplicate team name.
- Team creation limit exceeded.
- Non-admin attempts team administration.
- Duplicate active invitation.
- Invitation expired/cancelled/already accepted.
- Removing or demoting the last team administrator.
- Non-team member attempts project creation.
- Non-manager attempts project member management.
- Adding a project member who is not a team member.
- Removing or demoting the last project manager.

## Recommended Frontend Shape

### API and Store Modules

Add:

- `frontend/src/types/team.ts`
- `frontend/src/types/project.ts`
- `frontend/src/api/teams.ts`
- `frontend/src/api/projects.ts`
- `frontend/src/stores/team.ts`
- `frontend/src/stores/project.ts`

Use the auth store's loading/error pattern, but avoid one giant store if team and project flows become noisy. A team store can own teams, members, invitations, and my invitations; a project store can own projects, board, and project members.

### Routes and Views

Add or replace:

- `/app` -> Phase 2 start/selection view.
- `/teams/:teamId/members` -> team member management table.
- `/projects/:projectId/board` -> project board workspace.

Likely views:

- `frontend/src/views/TeamProjectStartView.vue`
- `frontend/src/views/TeamMembersView.vue`
- `frontend/src/views/ProjectBoardView.vue`

Likely components:

- `frontend/src/components/team/CreateTeamModal.vue`
- `frontend/src/components/team/InviteMemberModal.vue`
- `frontend/src/components/team/TeamMemberTable.vue`
- `frontend/src/components/project/CreateProjectModal.vue`
- `frontend/src/components/project/ProjectMemberDrawer.vue`
- `frontend/src/components/project/BoardColumn.vue`

### UI Risks

- Do not fake task cards. Empty board columns should be visually finished through real empty states, count labels, state copy, and disabled or absent task actions.
- Do not expose Phase 5 dashboard queues, reports, notifications, or activity feed as real data.
- Keep project member management in project context, preferably a drawer/modal from the board header.
- The team member management table should remain accessible: visible labels, button text or `aria-label`, focus states, and clear disabled/error states.
- Use `design-system/MASTER.md` and Phase 1 UI patterns. Add tokens rather than scattering new raw hex values.

## Planning Implications

Recommended plan split:

1. **Backend domain foundation:** models, enums, migration, permission helpers, team/project services, and backend tests for invariants.
2. **Backend API surface:** routers and schemas for team invitation/member flows, project creation/member flows, board retrieval, and integration tests.
3. **Frontend data and routing:** API modules, stores, protected routes, start/selection view, and basic navigation integration.
4. **Frontend management and board UI:** team member table, invitation UI, project creation, project board, project member drawer, empty board columns, and UI tests.

This split keeps schema/domain risks ahead of UI work and lets frontend consume stable typed contracts.

## Validation Architecture

### Automated Test Strategy

Use the existing test infrastructure:

- Backend quick command: `cd backend && uv run pytest`
- Frontend quick command: `cd frontend && npm run test:unit -- --run`
- Frontend type/build check: `cd frontend && npm run build`

Backend tests should cover:

- Team creation creates the creator as `TEAM_ADMIN`.
- Team name validation and duplicate handling.
- Team creation limit of five teams per user.
- Team invitation creation, duplicate active invitation rejection, cancellation, expiration handling, and acceptance after registration/login.
- Team role updates and removal/demotion restrictions for the last administrator.
- Project creation only by team members.
- Project creation creates creator as `PROJECT_MANAGER`.
- Project creation creates exactly five `board_columns` with status mapping and stable ordering.
- Project member additions are limited to team members.
- Project role updates and removal/demotion restrictions for the last project manager.
- Team admin project visibility without project edit permission.

Frontend tests should cover:

- `/app` routes authenticated users to the Phase 2 start/selection experience.
- No-team state shows a create-team primary action.
- Create project success navigates to `/projects/:projectId/board`.
- Project board renders five empty columns and no fake task cards.
- Team member table exposes invite, role change, remove/cancel states.
- Project member drawer supports adding team members and changing project roles.

### Manual Verification

Manual checks should include:

- Register/login as a demo user.
- Create a team and confirm creator is team admin.
- Invite an unregistered email, register as that email, and accept the invitation.
- Create a project and confirm direct navigation to the board.
- Confirm the board shows exactly five empty default columns.
- Confirm non-manager users cannot manage project members.

### Security Threat Model Inputs

Plan files must include threat model coverage for:

- Broken access control between teams and projects.
- Unauthorized role escalation.
- Removing the final team administrator or final project manager.
- Invitation hijacking via email mismatch or duplicate pending invite.
- Cross-team project/member data leakage.
- Fake completion data entering Phase 2 UI.

## Open Planning Risks

- `init.phase-op` currently identifies the phase name from the directory slug (`team-project-board`) rather than the roadmap Chinese name. Plan files should use the roadmap name `团队、项目与基础看板` in human-readable text.
- Phase 2 has UI scope and `workflow.ui_safety_gate` is enabled. Planning should not continue without a Phase 2 `UI-SPEC.md` unless the operator explicitly reruns with `--skip-ui`.
- GSD subagents are not installed in this Codex environment, so research was produced inline. Plans should still follow normal GSD artifact contracts.

## RESEARCH COMPLETE
