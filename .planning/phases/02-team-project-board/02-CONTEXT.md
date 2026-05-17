# Phase 2: 团队、项目与基础看板 - Context

**Gathered:** 2026-05-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 2 delivers the first real collaboration workspace after authentication: logged-in users can create teams, invite members, manage team roles, create projects, manage project membership, and enter a default project board workspace.

This phase must create real team, project, membership, invitation, and default board-column records. It does not implement task cards, task creation, work logs, blockers, acceptance submission, review actions, notifications, reports, recent-project routing, real email delivery, real Git integration, or AI/Agent review. Those belong to later phases.

</domain>

<decisions>
## Implementation Decisions

### 团队邀请形态

- **D-01:** Phase 2 uses demo-first email invitations: a team administrator enters an email and team role, and the system creates a pending invitation record.
- **D-02:** Do not send real email in Phase 2. The data model and service boundary should preserve a future extension point for real invitation links or mail delivery.
- **D-03:** An invitation may target an email that does not yet have a registered account.
- **D-04:** When a user registers with an invited email, the system should match pending invitations by email so the user can accept them naturally after registration/login.
- **D-05:** The inviter selects the team role at invitation time; after acceptance, that role takes effect directly.
- **D-06:** Team invitations must support `PENDING`, `ACCEPTED`, `EXPIRED`, and `CANCELLED` states.
- **D-07:** Pending invitations expire after 7 days by default.
- **D-08:** Team administrators can cancel pending invitations.
- **D-09:** At most one active pending invitation should exist for the same team/email pair.

### 团队角色与项目角色边界

- **D-10:** Phase 2 team roles are exactly two levels: `TEAM_ADMIN` and `TEAM_MEMBER`.
- **D-11:** The user who creates a team automatically becomes `TEAM_ADMIN`.
- **D-12:** Team administrators can invite members, view team members, adjust team roles, and remove team members.
- **D-13:** Phase 2 project roles are exactly two levels: `PROJECT_MANAGER` and `PROJECT_MEMBER`.
- **D-14:** The user who creates a project automatically becomes `PROJECT_MANAGER`.
- **D-15:** Detailed project roles such as technical lead, developer, and tester are deferred until later phases where task execution and review behavior need them.
- **D-16:** Team administrators may view projects under their team, but they do not automatically receive project edit or project-manager authority.
- **D-17:** Managing project members and project roles requires `PROJECT_MANAGER` authority for that project.
- **D-18:** Project members must come from existing team members. Project-level invitation of team-external users is out of scope for Phase 2.

### 项目创建后的默认入口

- **D-19:** After project creation succeeds, the frontend should navigate directly to the new project's board page.
- **D-20:** In Phase 2, `/app` should become a real guided start page instead of the Phase 1 foundation page.
- **D-21:** If the user has no teams, `/app` should prioritize an empty state and primary action for creating the first team.
- **D-22:** If the user has multiple teams or projects, the default entry should be a team/project selection page rather than automatically opening a recent or newest project.
- **D-23:** Do not implement last-visited project routing in Phase 2; that belongs naturally with later workspace/navigation work.
- **D-24:** The project board page should show the project title, member/role summary, project management affordances, and the default board columns.

### 基础看板真实程度

- **D-25:** Phase 2 does not allow board-column customization.
- **D-26:** Project creation must automatically create exactly five default board columns: 待办, 进行中, 待验收, 打回修改, 已完成.
- **D-27:** The empty board must show real empty states and must not include fake task cards or sample task data.
- **D-28:** Empty column copy may explain that the column structure is ready and tasks will be connected in a later phase, but it must remain user-facing and not read like implementation notes.
- **D-29:** Default board columns must be persisted as real `board_columns` records, created in the same project-creation transaction as the project and initial project membership.
- **D-30:** Each default board column maps one-to-one to a fixed task status: 待办 -> `TODO`, 进行中 -> `IN_PROGRESS`, 待验收 -> `IN_REVIEW`, 打回修改 -> `REJECTED`, 已完成 -> `DONE`.
- **D-31:** Phase 2 should establish the board/status structure that Phase 3 tasks and Phase 4 acceptance review will reuse without migration or remapping.

### 成员管理体验

- **D-32:** Team member management should use a table-oriented management page.
- **D-33:** The team members table should expose member identity, team role, joined/status information, invitation status where relevant, and administrator actions.
- **D-34:** Project member management should be reachable from the project board context, such as from a member summary or "manage members" action near the board header.
- **D-35:** Project member management should use a drawer or modal so project managers can manage members without leaving the board context.
- **D-36:** The project member management drawer/modal should support adding existing team members to the project and adjusting `PROJECT_MANAGER` / `PROJECT_MEMBER` roles.
- **D-37:** Removal and role-change operations must enforce minimum authority constraints in the backend, not only in the frontend.
- **D-38:** A team must always retain at least one `TEAM_ADMIN`.
- **D-39:** A project must always retain at least one `PROJECT_MANAGER`.
- **D-40:** A user must not be allowed to remove themselves from the last administrator or last project-manager position.

### the agent's Discretion

- Exact API route names, schema names, service decomposition, and frontend component names may be selected by the planner as long as they follow existing `/api/v1`, FastAPI service, Pinia, router, and `AppLayout` patterns.
- The planner may decide whether invitation acceptance is exposed as a dedicated "my invitations" page, a guided banner after login, or a focused team-entry screen, as long as pending invitations for the logged-in email are discoverable and accept/reject behavior is clear.
- The planner may choose table columns and drawer layout details as long as the UI remains an operational SaaS cockpit, follows `design-system/MASTER.md`, and avoids fake Phase 3/5 data.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### GSD Planning Baseline

- `.planning/PROJECT.md` — Project value, v1 boundaries, deferred scope, and locked MVP framing.
- `.planning/REQUIREMENTS.md` — Phase 2 requirements `TEAM-01..03` and `PROJ-01..03`, plus cross-phase boundaries.
- `.planning/ROADMAP.md` — Phase 2 goal, success criteria, notes, and explicit non-goals.
- `.planning/STATE.md` — Current project state and workflow settings.
- `.planning/config.json` — GSD workflow configuration.
- `.planning/phases/01-auth-foundation/01-CONTEXT.md` — Prior decisions to carry forward from Phase 1.
- `design-system/MASTER.md` — TTCS frontend visual system derived from `ui-ux-pro-max`; MUST read before frontend planning or implementation.

### Source Requirements and Design

- `01-requirements/02-srs.md` — SRS V2.4; team/project requirements, business rules, default board columns, and v1/v2 boundaries.
- `02-design/02-high-level-design.md` — Architecture, module boundaries, Team API, Project API, data domains, and permission model.
- `02-design/03-low-level-design.md` — Expected backend/frontend structure, project board route, permission helpers, and board/task status baseline.
- `02-design/01-task-acceptance-design.md` — Later acceptance model; Phase 2 board/status choices must not block evidence-gated completion.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `backend/app/models/user.py` — Existing SQLAlchemy model style for Phase 2 models.
- `backend/app/schemas/auth.py` — Existing Pydantic schema style for request/response objects.
- `backend/app/services/auth_service.py` — Existing service-layer pattern for transactional business actions.
- `backend/app/api/v1/router.py` and `backend/app/api/v1/auth.py` — Existing `/api/v1` router inclusion pattern.
- `backend/app/deps.py` — Existing `get_current_user` and database dependency pattern for protected endpoints.
- `frontend/src/layouts/AppLayout.vue` — Reusable protected application shell for team/project navigation.
- `frontend/src/router/index.ts` — Existing protected route guard and route registration pattern.
- `frontend/src/stores/auth.ts` — Existing Pinia store pattern.
- `frontend/src/styles/tokens.css` — Existing semantic token foundation.

### Established Patterns

- Backend code uses FastAPI, SQLAlchemy ORM, Pydantic schemas, service classes, and Alembic migrations.
- Protected backend endpoints should depend on `get_current_user`.
- Frontend code uses Vue 3, TypeScript, Vue Router, Pinia, Axios, Ant Design Vue, and lucide icons.
- JWT is currently stored in `localStorage` and loaded by the router guard through the auth store.
- UI work must use semantic tokens, visible labels, focus states, accessible controls, and no fake later-phase business data.

### Integration Points

- Backend should add team/project routers under `/api/v1`, likely with prefixes such as `/teams` and `/projects`.
- Phase 2 models should be imported into `backend/app/models/__init__.py` or the Alembic metadata path so migrations can detect them.
- Project creation should transactionally create project membership and default board columns.
- Frontend should replace the Phase 1 foundation route content with a Phase 2 start/selection experience and add project board routes such as `/projects/:projectId/board`.
- `AppLayout` sidebar/navigation should evolve from the single Phase 1 auth-foundation item into team/project navigation without exposing Phase 3/5 features as active data.

</code_context>

<specifics>
## Specific Ideas

- The preferred demo path is: login -> create first team -> invite/manage members -> create project -> land directly on the empty default board.
- The board should feel real because the project, members, roles, and columns are real records, even though task cards are not implemented yet.
- Team and project roles should stay intentionally small in Phase 2 so later task/acceptance semantics can add complexity only where it is useful.

</specifics>

<deferred>
## Deferred Ideas

- Real email sending and invitation links — future enhancement after the demo-first invitation data flow is stable.
- Project-level invitation for users outside the team — future enhancement if needed; Phase 2 keeps project membership inside team membership.
- Detailed project roles such as technical lead, developer, and tester — deferred until task execution or acceptance review requires behavior differences.
- Last-visited or recent-project routing — better suited to the later workspace/navigation phase.
- Board column customization, reordering, adding, or deleting — deferred because the MVP task state machine depends on fixed default states.
- Task cards, task creation, work logs, blockers, acceptance submission, review actions, notifications, reports, and activity feeds — later roadmap phases.

</deferred>

---

*Phase: 2-团队、项目与基础看板*
*Context gathered: 2026-05-17*
