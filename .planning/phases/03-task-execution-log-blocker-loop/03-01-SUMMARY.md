---
phase: 03-task-execution-log-blocker-loop
plan: 01
subsystem: backend
tags: [fastapi, sqlalchemy, alembic, pytest, task-domain]
requires:
  - phase: 02-team-project-board
    provides: project members, fixed board columns, project permission patterns
provides:
  - Task, participant, subtask, and dependency persistence
  - Task service invariants for Owner, participants, progress, dependencies, and status guardrails
  - Backend task-domain pytest coverage
affects: [phase-03-api, phase-04-acceptance-gates, phase-05-workbench]
tech-stack:
  added: []
  patterns: [service-layer domain invariants, task-state guard helper, dynamic Alembic-head guard tests]
key-files:
  created:
    - backend/app/models/task.py
    - backend/app/schemas/task.py
    - backend/app/services/task_state.py
    - backend/app/services/task_service.py
    - backend/alembic/versions/20260518_0003_create_task_execution_tables.py
    - backend/tests/test_task_execution.py
  modified:
    - backend/app/models/__init__.py
    - backend/app/services/permissions.py
    - backend/tests/conftest.py
    - backend/tests/test_migration_guard.py
key-decisions:
  - "Task progress is computed only from one-level subtasks; status does not synthesize pseudo-progress."
  - "Participant removal preserves the participant row with removed_at for future evidence/history references."
  - "Phase 3 status guardrails reserve IN_REVIEW, DONE, CLOSED, and DELETED transitions for later workflow services."
patterns-established:
  - "TaskService centralizes task-domain mutation rules and commits transactions per operation."
  - "Task permission helpers allow team-admin visibility through project rules but require Owner/project-manager/task participation for mutation."
requirements-completed: [TASK-01, TASK-02, TASK-03, TASK-04, TASK-05, TASK-06, TASK-07, TASK-08]
duration: 47 min
completed: 2026-05-18
---

# Phase 03 Plan 01: Task Domain Foundation Summary

**Backend task-domain foundation with task tables, Owner/participant invariants, one-level subtasks, dependency cycle rejection, and Phase 3 status guardrails**

## Performance

- **Duration:** 47 min
- **Started:** 2026-05-18T07:25:00Z
- **Completed:** 2026-05-18T08:12:15Z
- **Tasks:** 4
- **Files modified:** 11

## Accomplishments

- Added persistent task, participant, subtask, and dependency models plus Alembic migration.
- Added task schemas and permission helpers for visibility, Owner/project-manager mutation, and participant access.
- Implemented `TaskService` rules for Owner auto-participation, 5-person limit, soft delete, participant removal audit preservation, subtask progress, dependency cycles, and direct-DONE rejection.
- Added focused pytest coverage and repaired migration-guard tests for the new Alembic head.

## Task Commits

Each task was committed atomically:

1. **Task 03-01-01: Add task models and migration** - `afae3bd` (feat)
2. **Task 03-01-02: Add task schemas and permission helpers** - `c17a1b1` (feat)
3. **Task 03-01-03: Implement task service invariants and state guardrails** - `276235c` (feat)
4. **Task 03-01-04: Add backend task-domain tests** - `f97f0b2` (test)
5. **Plan verification fix: Migration guard follows current Alembic head** - `bf4023c` (fix)

## Files Created/Modified

- `backend/app/models/task.py` - Task, participant, subtask, dependency models and enum values.
- `backend/alembic/versions/20260518_0003_create_task_execution_tables.py` - Task execution tables and indexes.
- `backend/app/schemas/task.py` - Task create/update/public/detail/card/subtask/dependency schemas.
- `backend/app/services/permissions.py` - Task visibility and mutation permission helpers.
- `backend/app/services/task_state.py` - Phase 3 allowed transition rules.
- `backend/app/services/task_service.py` - Task-domain service operations and invariants.
- `backend/tests/test_task_execution.py` - Task-domain service and permission tests.
- `backend/tests/test_migration_guard.py` - Dynamic Alembic-head expectation for migration guard tests.

## Decisions Made

- Kept subtasks as one-level checklist rows and computed `Task.progress` as completed/total subtasks only.
- Preserved removed participants with `removed_at` instead of deleting rows, matching future evidence-history needs.
- Treated direct movement to `DONE`, `IN_REVIEW`, `REJECTED`, `CLOSED`, and `DELETED` as reserved outside ordinary Phase 3 task actions.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added early smoke test because the planned verification command targeted a not-yet-created file**
- **Found during:** Task 03-01-01
- **Issue:** `cd backend && uv run pytest -q tests/test_task_execution.py` failed because the file did not exist yet.
- **Fix:** Created an initial enum-contract test, then expanded it in Task 03-01-04.
- **Files modified:** `backend/tests/test_task_execution.py`
- **Verification:** `cd backend && uv run pytest -q tests/test_task_execution.py`
- **Committed in:** `afae3bd`

**2. [Rule 1 - Test Drift] Updated migration guard tests after adding a new Alembic head**
- **Found during:** Plan-level backend full suite
- **Issue:** `tests/test_migration_guard.py` still expected `20260517_0002` as head after the new task migration introduced `20260518_0003`.
- **Fix:** Read the active Alembic head dynamically in the test.
- **Files modified:** `backend/tests/test_migration_guard.py`
- **Verification:** `cd backend && uv run pytest -q`
- **Committed in:** `bf4023c`

---

**Total deviations:** 2 auto-fixed (1 blocking verification setup, 1 test drift).
**Impact on plan:** Both fixes were necessary to keep the planned verification gates truthful; no scope was expanded beyond the task-domain foundation.

## Issues Encountered

None outstanding. Full backend test suite passes.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Ready for Plan 03-02. The backend now has stable task-domain primitives for work-log/blocker APIs and board/detail payloads. Phase 4 acceptance submission/review tables were not created; only `acceptance_summary` is reserved on `tasks`.

---
*Phase: 03-task-execution-log-blocker-loop*
*Completed: 2026-05-18*
