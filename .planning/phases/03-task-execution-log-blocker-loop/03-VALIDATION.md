---
phase: 03
slug: task-execution-log-blocker-loop
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-05-18
---

# Phase 03 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest, Vitest, vue-tsc |
| **Config file** | `backend/pyproject.toml`, `frontend/package.json`, `frontend/vite.config.ts` |
| **Quick run command** | `cd backend && uv run pytest -q tests/test_task_execution.py` |
| **Full suite command** | `cd backend && uv run pytest -q && cd ../frontend && npm run typecheck && npm run test:unit -- --run && npm run build` |
| **Estimated runtime** | ~90 seconds |

---

## Sampling Rate

- **After every backend task commit:** Run `cd backend && uv run pytest -q tests/test_task_execution.py`
- **After every frontend task commit:** Run `cd frontend && npm run typecheck && npm run test:unit -- --run src/views/task-execution.spec.ts`
- **After every plan wave:** Run `cd backend && uv run pytest -q && cd ../frontend && npm run typecheck && npm run test:unit -- --run && npm run build`
- **Before `$gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 90 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | TASK-01, TASK-04, TASK-05 | T-03-01 | Project membership and Owner/participant rules enforced server-side | unit/API | `cd backend && uv run pytest -q tests/test_task_execution.py` | ✅ | ✅ green |
| 03-01-02 | 01 | 1 | TASK-06, TASK-07, TASK-08 | T-03-02 | State transitions, dependencies, and progress cannot be client-forged | unit/API | `cd backend && uv run pytest -q tests/test_task_execution.py` | ✅ | ✅ green |
| 03-02-01 | 02 | 2 | WORK-01, WORK-02, WORK-03 | T-03-03 | Work logs validate actor, date, hours, and code fields without external Git access | unit/API | `cd backend && uv run pytest -q tests/test_task_execution.py` | ✅ | ✅ green |
| 03-02-02 | 02 | 2 | WORK-04, WORK-05, WORK-06 | T-03-04 | Unresolved blockers prevent acceptance eligibility and preserve audit fields | unit/API | `cd backend && uv run pytest -q tests/test_task_execution.py` | ✅ | ✅ green |
| 03-03-01 | 03 | 3 | TASK-01, TASK-02, TASK-08 | T-03-05 | Frontend does not expose unauthorized or fake task actions | component/type | `cd frontend && npm run typecheck && npm run test:unit -- --run src/views/task-execution.spec.ts` | ✅ | ✅ green |
| 03-03-02 | 03 | 3 | WORK-01, WORK-04, WORK-05 | T-03-06 | Drawer and detail UI preserve blocker and work-log visibility without fake data | component/type | `cd frontend && npm run typecheck && npm run test:unit -- --run src/views/task-execution.spec.ts` | ✅ | ✅ green |
| 03-04-01 | 04 | 4 | TASK-01..08, WORK-01..06 | T-03-07 | End-to-end demo path uses persisted task, work-log, and blocker data | full suite | `cd backend && uv run pytest -q && cd ../frontend && npm run typecheck && npm run test:unit -- --run && npm run build` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers the phase:

- [x] `backend/tests/conftest.py` — shared in-memory DB fixture.
- [x] `backend/pyproject.toml` — pytest configured.
- [x] `frontend/package.json` — `typecheck`, `test:unit`, and `build` scripts configured.
- [x] `frontend/src/tests/setup.ts` — frontend unit test setup exists.

Wave 1 must create `backend/tests/test_task_execution.py`. Wave 3 must create `frontend/src/views/task-execution.spec.ts`.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Operational task-board flow feels usable in the live app | TASK-01, WORK-01, WORK-04 | Component tests cannot fully judge cockpit scan density and drawer ergonomics | Log in, open project board, create task, open drawer, write log, mark/resolve blocker, open `/tasks/:taskId` |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 90s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-05-18
