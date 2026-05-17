---
phase: 2
slug: team-project-board
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-05-17
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest, Vitest, vue-tsc/Vite build |
| **Config file** | `backend/pyproject.toml`, `frontend/package.json`, `frontend/vite.config.ts` |
| **Quick run command** | `cd backend && uv run pytest`; `cd frontend && npm run test:unit -- --run` |
| **Full suite command** | `cd backend && uv run pytest`; `cd frontend && npm run build`; `cd frontend && npm run test:unit -- --run` |
| **Estimated runtime** | ~60 seconds |

---

## Sampling Rate

- **After every backend task commit:** Run `cd backend && uv run pytest`
- **After every frontend task commit:** Run `cd frontend && npm run test:unit -- --run`
- **After every full-stack wave:** Run `cd backend && uv run pytest`, `cd frontend && npm run build`, and `cd frontend && npm run test:unit -- --run`
- **Before `$gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 90 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | TEAM-01 | T-02-01 | creator becomes `TEAM_ADMIN`; duplicate team names rejected | unit/integration | `cd backend && uv run pytest` | ❌ W0 | ⬜ pending |
| 02-01-02 | 01 | 1 | TEAM-02, TEAM-03 | T-02-02 / T-02-03 | only admins manage invitations/members; last admin protected | unit/integration | `cd backend && uv run pytest` | ❌ W0 | ⬜ pending |
| 02-01-03 | 01 | 1 | PROJ-01, PROJ-02, PROJ-03 | T-02-04 / T-02-05 | only team members create projects; creator becomes manager; five columns created | unit/integration | `cd backend && uv run pytest` | ❌ W0 | ⬜ pending |
| 02-02-01 | 02 | 2 | TEAM-01, TEAM-02, TEAM-03 | T-02-02 | team APIs enforce auth and role checks | integration | `cd backend && uv run pytest` | ❌ W0 | ⬜ pending |
| 02-02-02 | 02 | 2 | PROJ-01, PROJ-02, PROJ-03 | T-02-04 | project APIs enforce project manager/member boundaries | integration | `cd backend && uv run pytest` | ❌ W0 | ⬜ pending |
| 02-03-01 | 03 | 3 | TEAM-01, PROJ-01 | — | authenticated `/app` shows start/selection flow | unit | `cd frontend && npm run test:unit -- --run` | ❌ W0 | ⬜ pending |
| 02-03-02 | 03 | 3 | PROJ-03 | T-02-06 | board renders real empty columns and no fake task cards | unit/build | `cd frontend && npm run build && npm run test:unit -- --run` | ❌ W0 | ⬜ pending |
| 02-04-01 | 04 | 4 | TEAM-02, TEAM-03, PROJ-02 | T-02-02 / T-02-04 | management UI exposes allowed operations and handles forbidden/error states | unit/build | `cd frontend && npm run build && npm run test:unit -- --run` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠ flaky*

---

## Wave 0 Requirements

- [ ] `backend/tests/test_team_project.py` — tests for team, invitation, project, membership, and board-column invariants.
- [ ] `frontend/src/views/team-project.spec.ts` or focused view/component specs — tests for `/app`, project board, member management affordances, and empty board columns.
- [ ] Existing `backend/tests/conftest.py` remains the shared backend fixture source.
- [ ] Existing `frontend/src/tests/setup.ts` remains the frontend test setup source.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Full demo path from login to team/project/board | TEAM-01, TEAM-02, PROJ-01, PROJ-03 | Verifies cross-screen UX and navigation polish | Login, create a team, invite an email, create a project, confirm direct navigation to `/projects/:projectId/board` |
| Invitation acceptance by newly registered email | TEAM-02 | Depends on multi-account demo sequencing | Invite an unregistered email, logout, register with that email, accept pending invitation |
| Visual quality and responsive behavior | TEAM-03, PROJ-02, PROJ-03 | Automated tests cannot fully judge layout quality | Check desktop and mobile widths for no horizontal scroll, visible focus states, and no fake task cards |

---

## Validation Sign-Off

- [x] All tasks have automated verify targets or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all missing references
- [x] No watch-mode flags
- [x] Feedback latency target < 90s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
