---
phase: 02-team-project-board
plan: 05
subsystem: backend
tags: [fastapi, alembic, sqlite, migration-readiness, uat-gap]
requires:
  - phase: 02-team-project-board
    provides: Phase 2 team/project Alembic migration
provides:
  - Startup migration readiness guard
  - Direct migration readiness CLI
  - Regression coverage for stale and current Alembic revisions
  - Backend cold-start migration documentation
affects: [backend-api, local-demo, phase-02-uat]
tech-stack:
  added: []
  patterns: [fail-fast startup guard, alembic-head comparison, in-memory-test skip]
key-files:
  created:
    - backend/app/scripts/ensure_migrations.py
    - backend/tests/test_migration_guard.py
  modified:
    - backend/app/main.py
    - backend/README.md
key-decisions:
  - "The backend fails fast when a file-backed runtime database is behind Alembic head instead of serving Phase 2 APIs that later 500."
  - "The guard does not auto-run migrations at startup; developers get an explicit remediation command."
  - "In-memory SQLite is skipped so existing isolated unit tests keep using metadata-created schemas."
patterns-established:
  - "Migration readiness checks compare database heads to Alembic script heads before FastAPI serves traffic."
requirements-completed: [TEAM-01, TEAM-02, TEAM-03, PROJ-01, PROJ-02, PROJ-03]
gaps-closed:
  - "Cold start applies or requires Phase 2 schema before team/project APIs are used"
duration: 18 min
completed: 2026-05-18
---

# Phase 2 Plan 05: Cold Start Migration Guard Summary

**Closed the Phase 2 UAT cold-start schema gap with a startup migration guard, direct CLI check, docs, and regression tests.**

## Performance

- **Duration:** 18 min
- **Completed:** 2026-05-18
- **Tasks:** 4
- **Files modified:** 4

## Accomplishments

- Added `backend/app/scripts/ensure_migrations.py` to compare the configured database Alembic revision against migration script head.
- Wired the check into FastAPI lifespan startup so stale file-backed databases fail before API traffic is served.
- Preserved in-memory SQLite test behavior so existing API tests remain lightweight.
- Updated backend docs with the migration prerequisite, stale-schema symptom, direct check command, and remediation command.
- Added regression coverage for stale revision rejection, current head acceptance, in-memory skip behavior, and startup failure.

## Task Commits

1. **Tasks 1-4: Migration helper, startup guard, docs, tests** - `7b28b9d` (fix)

## Files Created/Modified

- `backend/app/scripts/ensure_migrations.py` - Alembic head comparison helper and CLI entry point.
- `backend/app/main.py` - FastAPI lifespan startup guard.
- `backend/tests/test_migration_guard.py` - Regression tests for stale/current/in-memory/startup behavior.
- `backend/README.md` - Cold-start migration workflow and Phase 2 route documentation.

## Verification

- `cd backend && uv run pytest -q tests/test_migration_guard.py` -> passed, 4 tests.
- `cd backend && uv run pytest -q` -> passed, 28 tests.
- `cd backend && uv run alembic upgrade head` -> passed.
- `cd backend && uv run python -m app.scripts.ensure_migrations` -> passed, database at latest revision.
- `cd backend && uv run python - <<'PY' ... TestClient(create_app()).get('/api/v1/health') ... PY` -> passed with `200 {'status': 'ok', 'service': 'ttcs-api'}`.

## Deviations from Plan

None - plan executed as written.

## Issues Encountered

The first focused pytest command was run from `backend/` with a repo-root-prefixed path, so pytest could not find `backend/tests/test_migration_guard.py`. Re-running with `tests/test_migration_guard.py` passed.

## User Setup Required

None for already-migrated local databases. If a local file-backed database is stale, run:

```bash
cd backend && uv run alembic upgrade head
```

## Next Phase Readiness

The Phase 2 UAT blocker is closed. Cold-starting against a stale schema now fails early with an actionable migration command instead of allowing team/project endpoints to fail at request time.

## Self-Check: PASSED

- Key files exist on disk.
- Production commit exists for `02-05`.
- All task acceptance criteria are covered by regression tests, CLI checks, and README documentation.
- Plan-level verification commands passed.

---
*Phase: 02-team-project-board*
*Completed: 2026-05-18*
