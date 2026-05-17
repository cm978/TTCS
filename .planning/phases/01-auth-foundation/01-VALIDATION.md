---
phase: 1
slug: auth-foundation
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-05-17
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Backend framework** | `pytest` + FastAPI `TestClient` or `httpx` |
| **Frontend framework** | `vitest` + Vue Test Utils |
| **Config files** | `backend/pyproject.toml`, `frontend/vite.config.ts`, `frontend/package.json` |
| **Backend quick run** | `cd backend && pytest -q` |
| **Frontend quick run** | `cd frontend && npm run test:unit -- --run` |
| **Full suite command** | `cd backend && pytest -q && cd ../frontend && npm run typecheck && npm run test:unit -- --run && npm run build` |
| **Estimated runtime** | ~60-120 seconds after dependencies are installed |

## Sampling Rate

- **After every task commit:** run the relevant backend or frontend quick command.
- **After every plan wave:** run the full suite command when both app halves exist.
- **Before `$gsd-verify-work`:** backend tests, frontend typecheck, frontend unit tests, frontend build, and manual auth smoke must pass.
- **Max feedback latency:** keep quick checks under 60 seconds where practical.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 0 | ARCH-01, ARCH-02, ARCH-03, ARCH-04 | T-01-ENV | local config uses env examples, no secrets committed | smoke/static | `docker compose config` | ❌ W0 | ⬜ pending |
| 01-01-02 | 01 | 0 | ARCH-02, AUTH-04 | T-01-DB | migration creates user table with hashed password field only | integration | `cd backend && pytest -q` | ❌ W0 | ⬜ pending |
| 01-02-01 | 02 | 1 | AUTH-01, AUTH-04 | T-01-PWD | plaintext password never persists or returns | API/integration | `cd backend && pytest -q` | ❌ W0 | ⬜ pending |
| 01-02-02 | 02 | 1 | AUTH-02 | T-01-JWT | valid credentials issue expiring JWT only | API/integration | `cd backend && pytest -q` | ❌ W0 | ⬜ pending |
| 01-02-03 | 02 | 1 | AUTH-03 | T-01-AUTHZ | `/me` rejects missing/invalid token and returns current user for valid token | API/integration | `cd backend && pytest -q` | ❌ W0 | ⬜ pending |
| 01-03-01 | 03 | 2 | ARCH-01, AUTH-01 | T-01-UI | register form validates input and does not expose raw backend errors | component | `cd frontend && npm run test:unit -- --run` | ❌ W0 | ⬜ pending |
| 01-03-02 | 03 | 2 | ARCH-01, AUTH-02 | T-01-TOKEN | login stores bearer token, refresh recovers session, logout clears token | store/router | `cd frontend && npm run test:unit -- --run` | ❌ W0 | ⬜ pending |
| 01-03-03 | 03 | 2 | AUTH-03, ARCH-01 | T-01-ROUTE | protected route redirects anonymous users and shows `/me` user when authenticated | router/component | `cd frontend && npm run test:unit -- --run` | ❌ W0 | ⬜ pending |
| 01-04-01 | 04 | 3 | AUTH-01, AUTH-02, AUTH-03, AUTH-04, ARCH-01, ARCH-02, ARCH-03, ARCH-04 | T-01-SMOKE | full local stack proves register/login/me/logout path | full/manual + automated | full suite command | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

## Wave 0 Requirements

- [ ] `backend/tests/` contains initial auth API tests.
- [ ] `backend/tests/conftest.py` provides independent test database/session fixtures.
- [ ] `frontend/src/**/*.spec.ts` or `frontend/tests/` contains auth store/router tests.
- [ ] `backend/pyproject.toml` defines pytest dependencies and commands.
- [ ] `frontend/package.json` defines `test:unit`, `typecheck`, and `build`.

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Full local multi-process run | ARCH-01, ARCH-02, ARCH-03, ARCH-04 | Requires Docker services plus backend and frontend dev servers | Run Docker, backend, frontend; register; login; refresh protected page; logout; revisit protected route |
| Visual polish and responsive shell | ARCH-01 | Requires human design judgment against `01-UI-SPEC.md` | Check 375px, 768px, 1024px, and 1440px layouts for no horizontal scroll, visible labels, focus states, loading/error states |

## Validation Sign-Off

- [x] All tasks have automated verify or Wave 0 dependencies.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify.
- [x] Wave 0 covers all missing references.
- [x] No watch-mode flags in required validation commands.
- [x] Feedback latency target documented.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** approved 2026-05-17

