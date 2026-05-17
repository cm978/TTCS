---
phase: 01-auth-foundation
plan: 02
subsystem: auth
tags: [fastapi, jwt, bcrypt, sqlalchemy, alembic]
requires:
  - phase: 01-01
    provides: FastAPI app, SQLAlchemy base, Alembic foundation
provides:
  - User model and users migration
  - Registration, login, and `/me` endpoints
  - bcrypt password hashing
  - JWT bearer token issuance and validation
  - Local demo user seed command
affects: [frontend-auth, future-permissions]
tech-stack:
  added: [python-jose, passlib, bcrypt, email-validator]
  patterns: [auth-service, current-user dependency, safe public schemas]
key-files:
  created: [backend/app/api/v1/auth.py, backend/app/models/user.py, backend/app/core/security.py, backend/app/services/auth_service.py, backend/tests/test_auth.py]
  modified: [backend/app/api/v1/router.py, backend/pyproject.toml]
key-decisions:
  - "Use JWT bearer tokens with a 24-hour default lifetime."
  - "Use bcrypt hashes and never return password fields in API responses."
patterns-established:
  - "Auth endpoints delegate to `AuthService`."
  - "Protected endpoints use a reusable `get_current_user` dependency."
requirements-completed: [AUTH-01, AUTH-02, AUTH-03, AUTH-04, ARCH-02, ARCH-03, ARCH-04]
duration: 25min
completed: 2026-05-17
---

# Phase 1 Plan 02 Summary

**Database-backed email/password auth with bcrypt hashes, JWT bearer login, protected `/me`, and one-user dev seed**

## Performance

- **Started:** 2026-05-17T06:20:00Z
- **Completed:** 2026-05-17T06:39:27Z
- **Tasks:** 4/4
- **Files modified:** 15+

## Accomplishments

- Added `users` table migration and `User` SQLAlchemy model.
- Implemented `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, and `GET /api/v1/auth/me`.
- Added bcrypt hashing and JWT helpers.
- Added independent backend tests for registration, duplicate email, login, `/me`, malformed token, and expired token.
- Added local/dev-only seed command for a single demo user.

## Task Commits

1. **Plan 02 work** - `051df0c` (`feat(01): implement auth foundation`)

## Files Created/Modified

- `backend/app/api/v1/auth.py` - auth REST endpoints.
- `backend/app/core/security.py` - password hashing and JWT helpers.
- `backend/app/deps.py` - reusable current-user dependency.
- `backend/app/models/user.py` - user persistence model.
- `backend/tests/test_auth.py` - auth behavior coverage.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Pinned bcrypt below 4.0**
- **Found during:** backend test run.
- **Issue:** `passlib` failed with installed `bcrypt==5.0.0` during hash backend detection.
- **Fix:** Added `bcrypt>=3.2.0,<4.0.0` to backend dependencies and regenerated `uv.lock`.
- **Files modified:** `backend/pyproject.toml`, `backend/uv.lock`.
- **Verification:** `cd backend && uv run pytest -q` passes.
- **Committed in:** `051df0c`.

**2. [Rule 3 - Blocking] Changed default demo email to a valid reserved example domain**
- **Found during:** seed command verification.
- **Issue:** `demo@ttcs.local` was rejected by `email-validator`.
- **Fix:** Changed default demo address to `demo@example.com`.
- **Files modified:** `.env.example`, `backend/app/scripts/seed_demo_user.py`.
- **Verification:** `uv run python -m app.scripts.seed_demo_user` created the local demo user.
- **Committed in:** `051df0c`.

**Total deviations:** 2 auto-fixed blocking issues.  
**Impact on plan:** Both fixes were required for the planned auth path; no scope expansion.

## Issues Encountered

- Backend tests show a `passlib` Python 3.13 `crypt` deprecation warning from a dependency. It does not fail tests.

## User Setup Required

None beyond local dependency installation.

## Next Phase Readiness

Frontend can use the stable `/api/v1/auth/*` API and bearer token contract.

---
*Phase: 01-auth-foundation*
*Completed: 2026-05-17*

