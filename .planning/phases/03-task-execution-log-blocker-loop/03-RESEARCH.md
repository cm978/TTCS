# Phase 3: 任务执行、日志与阻塞闭环 - Research

## RESEARCH COMPLETE

**Phase:** 03 - 任务执行、日志与阻塞闭环  
**Date:** 2026-05-18  
**Purpose:** Identify what the planner needs to know before creating executable Phase 3 plans.

## Executive Summary

Phase 3 should be planned as a vertical MVP extension of the existing Phase 2 board, not as a pure backend schema phase. The safest plan shape is:

1. Add task-domain backend models, migration, schemas, permission helpers, and services.
2. Expose project-board task data, task detail, participant/subtask/dependency, and work-log/blocker APIs.
3. Replace empty board columns with real medium-density task cards, an editable drawer, and `/tasks/:taskId` detail route.
4. Add backend and frontend tests around permission boundaries, objective progress, blockers, and no-fake-data UI behavior.

The central implementation risk is not CRUD volume. It is preserving the product invariant: task completion cannot be faked. Phase 3 must produce trustworthy subtask, work-log, and blocker data for Phase 4 acceptance gates while not implementing Phase 4 Review actions early.

## Source Inputs

- `.planning/phases/03-task-execution-log-blocker-loop/03-CONTEXT.md` — locked user decisions D-01..D-41.
- `.planning/ROADMAP.md` — Phase 3 goal, success criteria, and `**Mode:** mvp`.
- `.planning/REQUIREMENTS.md` — `TASK-01..08` and `WORK-01..06`.
- `01-requirements/02-srs.md` — task/work-log/blocker requirements.
- `01-requirements/05-change-request-001.md` — work-log, multi-participant, blocker, and code-field change request.
- `02-design/01-task-acceptance-design.md` — evidence-gated acceptance model that Phase 3 feeds.
- `02-design/02-high-level-design.md` — task/work-log API groups, permission matrix, and risk handling.
- `02-design/03-low-level-design.md` — enums, model sketches, service methods, status machine, UI route/component guidance.
- `design-system/MASTER.md` — frontend cockpit style and accessibility rules.

## Existing Code Patterns

### Backend

- Models live under `backend/app/models/` and are exported from `backend/app/models/__init__.py` so `Base.metadata.create_all()` and Alembic metadata see them.
- Existing SQLAlchemy models use integer primary keys, string enum values, `created_at` / `updated_at`, and explicit indexes/unique constraints.
- Services live under `backend/app/services/` and encapsulate business rules, transaction commits, and domain-specific errors.
- API routers live under `backend/app/api/v1/`; protected routes depend on `get_current_user` and `get_db`.
- Existing project endpoints map domain errors to `403`, `404`, `409`, and `400` through local error helper functions.
- Tests use in-memory SQLite through `backend/tests/conftest.py`; every new model must be imported there or via `app.models` so `Base.metadata.create_all()` creates tables.
- Existing backend verification command is `cd backend && uv run pytest -q`.

### Frontend

- API wrappers live under `frontend/src/api/`, Pinia stores under `frontend/src/stores/`, and TypeScript domain types under `frontend/src/types/`.
- `ProjectBoardView.vue` currently loads a board and renders `BoardColumn` components with real persisted columns but no tasks.
- `BoardColumn.vue` is the main Phase 3 insertion point for real task cards.
- `ProjectMemberDrawer.vue` demonstrates the current Ant Design Vue drawer pattern for project-context editing.
- Routes are registered in `frontend/src/router/index.ts`; Phase 3 should add protected `/tasks/:taskId`.
- Existing component tests use Vitest and `@vue/test-utils`; verification commands are `cd frontend && npm run typecheck && npm run test:unit -- --run && npm run build`.

## Recommended Planning Shape

### Plan 03-01 — Backend Task Domain Foundation

Create the database and service foundation in one backend-first vertical slice:

- `backend/app/models/task.py`
- `backend/app/schemas/task.py`
- `backend/app/services/task_service.py`
- `backend/app/services/task_state.py` or equivalent internal state-machine helper
- permission helpers extending `backend/app/services/permissions.py`
- Alembic migration `20260518_0003_create_task_execution_tables.py`
- model exports and test fixture imports

This plan should cover task creation/edit/soft-delete, Owner as default participant, participant limit, one-level subtasks, dependencies, status transition guardrails, and objective progress calculation.

### Plan 03-02 — Backend Work Logs, Blockers, and Board API

Layer work logs and blocker behavior on top of task foundation:

- `WorkLogService` with create/update/soft-delete/list/resolve blocker behavior.
- Task board response including tasks grouped by existing board statuses.
- Task detail response including participants, subtasks, dependencies, work logs, and blocker summary.
- Backend tests proving future-date rejection, 0.5..24 hour validation, blocked reason length, multiple unresolved blockers, resolver permissions, and unresolved blockers preventing acceptance eligibility later.

This plan should not build Phase 4 acceptance submission endpoints, but it should make blocker and work-log data queryable for them.

### Plan 03-03 — Frontend Task Board, Drawer, and Detail Route

Replace Phase 2 empty board placeholders with real task execution UI:

- `frontend/src/types/task.ts`
- `frontend/src/api/tasks.ts`
- `frontend/src/stores/task.ts`
- task card, task drawer, task detail view, work-log form/list, subtask checklist components
- update `ProjectBoardView.vue`, `BoardColumn.vue`, and `frontend/src/router/index.ts`

The UI should follow `design-system/MASTER.md`: medium-density operational cards, blocker as the strongest visual signal, semantic status tokens, visible labels, loading/error/disabled states, 44px targets where practical, no emoji structural icons, no fake Phase 5 dashboard data.

### Plan 03-04 — Integration, Demo Seed, and Verification Hardening

Use a final integration plan to connect backend/frontend behavior and ensure the demo path is reliable:

- Ensure seed/demo data only creates real Phase 1/2/3 entities if adding Phase 3 demo data; no fake UI-only cards.
- Add or update README smoke steps for creating a task, writing a work log, marking/resolving a blocker, and opening `/tasks/:taskId`.
- Run backend and frontend verification.
- Confirm Phase 4/5 boundaries are not crossed: no acceptance Review actions, no notification center, no reports.

## Key Design Constraints for the Planner

- `TaskStatus` should include `TODO`, `IN_PROGRESS`, `IN_REVIEW`, `REJECTED`, `DONE`, `CLOSED`, and `DELETED`, but board columns only display the five Phase 2 statuses by default.
- Phase 3 can allow only safe user-driven state transitions such as `TODO -> IN_PROGRESS`; `IN_PROGRESS/REJECTED -> IN_REVIEW` must be reserved for Phase 4 acceptance submission.
- `DONE` should not be reachable from ordinary Phase 3 task actions.
- Owner must automatically be a participant and count toward the 5-person participant limit.
- Removing a participant should remove current participation only; historical work logs and blocker records remain.
- Subtasks are one-level checklist items. Progress is computed only from completed subtasks / total subtasks.
- Do not create manual progress editing.
- Work-log blocker records are the source of truth; task-level blocked fields are query/display denormalization.
- Multiple unresolved blockers can coexist; task card shows the latest unresolved blocker summary.
- Resolver permissions are blocker creator, task Owner, or project manager.
- Blocker resolution requires a note of at least 10 characters.
- Code fields on work logs are optional text only; no Git API calls and no strict Git validation.
- Work-log dates cannot be in the future.
- Work logs are soft-deletable/editable by creator with audit fields.

## Risk Notes

| Risk | Planning Response |
|------|-------------------|
| Phase 3 accidentally implements Phase 4 acceptance actions | Add must-have constraints that `IN_REVIEW`, `DONE`, acceptance submission, and review endpoints are not completed in Phase 3 except as reserved fields/data. |
| Board API becomes too large in one task | Split backend task foundation from board/work-log API and make frontend depend on stable response schemas. |
| Blocker denormalization drifts from work-log truth | Plan service methods that recompute current blocker summary after create/resolve/update/soft-delete operations. |
| Participant removal breaks historical evidence | Keep historical `work_logs.user_id` and blocker fields immutable; never cascade-delete history from participant removal. |
| One-level subtask decision conflicts with SRS 3-level wording | Document Phase 3 implementation as one-level UI with 3-level nesting deferred. Requirements coverage should still cite `TASK-06` with a scoped MVP interpretation. |
| UI card density hurts mobile layout | Require responsive card/list behavior, no horizontal mobile scroll outside intentional board scrolling, and semantic compact chips. |

## Validation Architecture

Phase 3 has enough backend rules and frontend behavior to require automated validation at every plan boundary.

### Backend Unit/API Coverage

- `backend/tests/test_task_execution.py` should cover model/service/API behavior for task creation, participant limit, Owner default participation, permissions, status guardrails, soft delete, subtasks, dependencies, progress, work-log validation, blocker lifecycle, and board/detail payloads.
- Backend quick command: `cd backend && uv run pytest -q tests/test_task_execution.py`
- Backend full command: `cd backend && uv run pytest -q`

### Frontend Unit/Type Coverage

- `frontend/src/views/task-execution.spec.ts` or equivalent should cover task store API flows, board card rendering, drawer behavior, detail route linking, light work-log state, and blocker-priority display.
- Frontend quick command: `cd frontend && npm run test:unit -- --run src/views/task-execution.spec.ts`
- Frontend full command: `cd frontend && npm run typecheck && npm run test:unit -- --run && npm run build`

### Manual Smoke Coverage

Manual smoke should remain short and demo-facing:

1. Log in.
2. Open a project board.
3. Create a task with Owner and participants.
4. Open drawer from card.
5. Add a work log.
6. Mark blocker from a work log.
7. See blocked card state.
8. Resolve blocker with required note.
9. Open `/tasks/:taskId`.

## Planner Checklist

- Every plan must cite the relevant `TASK-*` / `WORK-*` requirement IDs in frontmatter.
- Every plan must include a `<threat_model>` block because security enforcement is enabled by default.
- Every task must include concrete `<read_first>` and `<acceptance_criteria>` sections.
- Plans should be wave-based: backend foundation first, dependent API/work-log integration second, frontend UI after stable schemas, integration verification last.
- Frontend plans must read `design-system/MASTER.md` and avoid raw scattered colors, fake data, and emoji structural icons.

