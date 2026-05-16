# TTCS

## What This Is

TTCS (Team Task Collaboration System) is a web-based team task collaboration system for small software teams. For the current milestone, it is a course/demo-first MVP that proves a real delivery loop: daily standup visibility, personal execution queues, work logs, blocker reporting, evidence-gated task submission, and Owner/project-manager review.

It is not just a generic task board. The product should demonstrate why a task is considered complete by preserving work logs, document or code evidence, acceptance submissions, review decisions, rejection reasons, and immutable acceptance history.

## Core Value

Tasks can only become complete after traceable evidence and human acceptance prove the work is actually deliverable.

## Requirements

### Validated

(None yet - ship to validate)

### Active

- [ ] Users can register, log in, maintain a basic profile, and access the system through JWT-authenticated sessions.
- [ ] Teams can be created, members can be invited, and team/project roles can govern permissions.
- [ ] Projects can be created with members, project roles, and default board columns: TODO, IN_PROGRESS, IN_REVIEW, REJECTED, DONE.
- [ ] Project members can create, edit, soft-delete, assign, and track tasks with owners, participants, priorities, deadlines, subtasks, dependencies, and task types.
- [ ] Tasks support multiple participants with a maximum of 5 participants per task while preserving a clear owner.
- [ ] Members can record work logs with work content, hours, optional code reference fields, and blocker status.
- [ ] Blockers are risk markers, not primary task status; unresolved blockers prevent acceptance submission and appear in standup/blocker reports.
- [ ] Task completion uses a state machine from TODO to IN_PROGRESS to IN_REVIEW to DONE, with REJECTED as the review failure path and CLOSED for later archival.
- [ ] General, document, and code tasks use different acceptance gates before submission.
- [ ] General tasks require completed subtasks or an acceptance summary, at least one valid work log, no unresolved blocker, eligible submitter permission, and a summary of at least 10 characters.
- [ ] Document tasks require the general gate plus at least one accessible document or attachment evidence item.
- [ ] Code tasks require the general gate plus at least one Commit, PR/MR, or code review record; unresolved code-review comments must be zero when review records are used.
- [ ] Participants can submit tasks for acceptance but cannot directly mark them complete.
- [ ] Owners and project managers can approve, reject, or request more evidence for submitted tasks.
- [ ] Acceptance submissions, gate snapshots, reviews, rejection reasons, and evidence references are audit records and must not be overwritten.
- [ ] The personal workspace provides action queues for today's tasks, missing work logs, blocked tasks, tasks ready for acceptance submission, tasks awaiting my review, and rejected tasks.
- [ ] Notifications and activity records cover task assignment, mentions, blocker updates, acceptance submission, approval, rejection, and evidence requests.
- [ ] Reports provide project progress, task distribution, work-hour statistics, blocker reports, and basic acceptance statistics.
- [ ] Document management supports upload, download, soft delete, metadata, access control, and linking documents as task evidence.
- [ ] Code evidence supports manual or simulated Commit, PR/MR, and code-review records for MVP acceptance evidence.
- [ ] The frontend uses Vue 3, TypeScript, Vite, Pinia, Vue Router, Axios, and Ant Design Vue.
- [ ] The backend uses Python 3.10+, FastAPI, SQLAlchemy, MySQL 8.0+, Redis 7+, REST APIs, JWT, and WebSocket notifications.
- [ ] The first implementation stays monolithic: one FastAPI backend, static frontend deployment, MySQL, Redis, and local or object-storage-compatible file storage.

### Out of Scope

- Real GitHub/GitLab webhook synchronization - deferred to phase 2; MVP may use manual or simulated code evidence.
- Real AI/Agent code review calls - deferred to phase 2; AI/Agent review may be represented only by reserved interfaces or data structures.
- Full rule engine for acceptance policies - deferred; MVP uses explicit hard-coded gate rules by task type.
- External calendar synchronization, iCal import/export, and CalDAV/Google Calendar integration - deferred to phase 2.
- Member homepage analytics and full member timeline - deferred to phase 2.
- Document versioning, archive strategy, capacity management, and bulk organization - deferred to phase 2.
- Multi-language UI - deferred; MVP is Chinese-first.
- Mobile app - out of current scope; responsive web is sufficient for MVP.
- CI/CD integration - deferred beyond the current MVP.
- Microservice split - unnecessary for the demo/MVP goal and would slow delivery.

## Context

The current source documents are:

- `01-requirements/02-srs.md` V2.4, which defines the current requirements baseline and explicitly narrows the project to an MVP delivery loop before phase-2 expansion.
- `02-design/01-task-acceptance-design.md`, which introduces the evidence gate plus human review completion model.
- `02-design/02-high-level-design.md`, which defines the system architecture, module boundaries, core flows, data domains, API groups, and phase boundaries.
- `02-design/03-low-level-design.md`, which details backend/frontend structure, enums, state machines, services, interfaces, and acceptance algorithms.
- `01-requirements/05-change-request-001.md`, which adds work logs, multi-participant tasks, blocker reporting, and Git-field reservation.
- `01-requirements/01-project-charter.md`, which originally excluded code repository integration from the current period; the current SRS resolves this by allowing only manual or simulated code evidence in MVP and deferring real Git integration.

The product is meant to support a realistic work rhythm:

1. A member starts from the personal workspace action queue.
2. They move tasks through the project board.
3. They record work logs and blocker status.
4. They attach or link delivery evidence.
5. They submit the task for acceptance only after gate checks pass.
6. The Owner or project manager reviews, approves, rejects, or requests more evidence.
7. Reports and workspace queues expose delivery risk, blocker load, acceptance quality, and progress.

## Constraints

- **Scope**: Current milestone is demo-first MVP - prioritize a coherent acceptance workflow over broad platform completeness.
- **Architecture**: Use a frontend/backend split with Vue 3 and FastAPI - this is fixed by the current SRS and design documents.
- **Backend stack**: Python 3.10+, FastAPI, SQLAlchemy, MySQL 8.0+, Redis 7+ - maintain consistency with SRS V2.4.
- **Frontend stack**: Vue 3.3+, TypeScript, Vite 5.x, Pinia, Vue Router 4.x, Axios, Ant Design Vue 4.x - maintain consistency with SRS V2.4.
- **API style**: RESTful `/api/v1` JSON APIs plus WebSocket notifications.
- **Authentication**: JWT bearer tokens with bcrypt password hashing.
- **Storage**: MVP can use local compatible storage or object storage for files, but metadata and permissions must remain in the database.
- **State integrity**: Task status changes, acceptance submission, review decisions, and evidence snapshots must be transactional where they affect completion state.
- **Auditability**: Acceptance submission and review history must be append-only rather than overwritten.
- **Permissions**: Completion authority belongs to Owner or project manager; automatic systems and participants cannot directly complete a task.
- **Code evidence**: MVP code evidence is manual or simulated; do not implement real Git platform synchronization as a phase-1 dependency.
- **Language**: MVP UI and documentation are Chinese-first.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Treat TTCS as a demo-first MVP rather than a full platform build | The current documents emphasize proving the delivery loop first and deferring platform expansion | - Pending |
| Make evidence-gated acceptance the core product value | This differentiates TTCS from a plain task board and creates a verifiable definition of done | - Pending |
| Keep blockers as a risk marker instead of a primary task state | Avoids state-machine bloat while preserving blocker reporting and acceptance gating | - Pending |
| Allow only manual or simulated code evidence in MVP | Reconciles the SRS code-evidence requirement with the charter's exclusion of real Git integration | - Pending |
| Defer real AI/Agent review to phase 2 | The design says AI/Agent review is auxiliary and must not own final completion authority | - Pending |
| Use a monolithic FastAPI backend for MVP | Faster delivery and simpler transaction boundaries suit the demo-first scope | - Pending |
| Model phases as vertical MVP slices | Each phase should produce an end-to-end user-visible capability instead of disconnected technical layers | - Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `$gsd-transition`):
1. Requirements invalidated? -> Move to Out of Scope with reason
2. Requirements validated? -> Move to Validated with phase reference
3. New requirements emerged? -> Add to Active
4. Decisions to log? -> Add to Key Decisions
5. "What This Is" still accurate? -> Update if drifted

**After each milestone** (via `$gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check - still the right priority?
3. Audit Out of Scope - reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-17 after initialization*
