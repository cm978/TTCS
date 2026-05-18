# Phase 3: 任务执行、日志与阻塞闭环 - Context

**Gathered:** 2026-05-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 3 turns the Phase 2 empty project board into a real task execution workspace. Project members can create and advance tasks, assign Owner and participants, manage lightweight subtasks and dependencies, write work logs, and expose blockers as delivery risk.

This phase must create real task, participant, subtask, dependency, work-log, and blocker data that Phase 4 acceptance gates and Phase 5 workbench/reporting can reuse. It does not implement full acceptance submission, Owner/project-manager Review, evidence snapshotting, notification center, project reports, real Git integration, AI/Agent review, or custom board-column workflows.

</domain>

<decisions>
## Implementation Decisions

### 任务详情承载方式

- **D-01:** Task cards use a combined drawer plus full detail page model.
- **D-02:** Clicking a board task card should open an editable task drawer first.
- **D-03:** The drawer handles high-frequency execution actions: editing basic task fields, adjusting participants, changing status, writing work logs, and marking or resolving blockers.
- **D-04:** The full detail page is for complete context: subtasks, dependencies, full work-log history, blocker history, and future Phase 4 acceptance/evidence panels.
- **D-05:** The drawer should guide users to the full detail page for complex structures such as subtasks, dependencies, full history, and future acceptance/evidence sections.
- **D-06:** Full task details must support direct access through `/tasks/:taskId`, so future workbench, notification, and report links can deep-link to a task.

### 任务参与者与 Owner 行为

- **D-07:** The task Owner is automatically added as a participant when a task is created.
- **D-08:** The Owner counts toward the maximum of 5 task participants.
- **D-09:** Owner and project managers can add or remove task participants.
- **D-10:** Ordinary participants cannot modify the participant list.
- **D-11:** A participant who has written work logs may still be removed from the current participant list.
- **D-12:** Removing a participant must not delete or rewrite historical work logs, blocker records, activity history, or future evidence references.
- **D-13:** A task may have only the Owner as its sole participant.

### 子任务与进度表达

- **D-14:** Phase 3 subtasks are lightweight checklist items, not separately assigned mini-tasks.
- **D-15:** Subtasks should include only necessary execution and audit fields such as title, completion state, completed-by, completed-at, and sort order.
- **D-16:** Phase 3 implements only one subtask level. The SRS "up to 3 levels" requirement is intentionally deferred to a later enhancement unless planning finds a low-risk way to reserve it without exposing nested UI.
- **D-17:** Task progress is calculated only from subtask completion ratio: completed subtasks divided by total subtasks.
- **D-18:** Do not allow manual task progress editing.
- **D-19:** If a task has no subtasks, do not invent status-based pseudo-progress such as 50% or 90%; show task status, work-log state, and blocker state instead.
- **D-20:** The task model should reserve or expose an acceptance-summary field for Phase 4. When a task has no subtasks, Phase 4 acceptance submission should require an acceptance summary of at least 10 characters.

### 阻塞记录与解除方式

- **D-21:** Blockers are work-log driven. A user creates a blocker by writing a work log marked as blocked with a reason.
- **D-22:** The source work log stores blocker reason, blocker creator, resolution information, and audit fields.
- **D-23:** The task should redundantly store current blocker state, such as `is_blocked` and the current/latest unresolved blocker summary, to support board display, acceptance checks, and later reports.
- **D-24:** Multiple unresolved blockers may exist on the same task at the same time.
- **D-25:** If multiple unresolved blockers exist, the board card displays the latest unresolved blocker summary while the detail page exposes full blocker history.
- **D-26:** A task is blocked, and cannot submit acceptance later, while any unresolved blocker exists.
- **D-27:** A blocker can be resolved by the blocker creator, the task Owner, or a project manager.
- **D-28:** Resolving a blocker must record resolver, resolved-at timestamp, and a resolution note of at least 10 characters.

### 看板任务卡信息密度

- **D-29:** Board task cards should be medium-density execution cards, not minimal placeholders or overloaded detail panels.
- **D-30:** Cards should show title, task type, priority, Owner, participant avatars/count, due date, subtask progress, blocker signal, and lightweight work-log state.
- **D-31:** Blocker state is the most prominent risk signal on the card. Overdue state and priority are secondary signals.
- **D-32:** Cards should show lightweight work-log state such as "today logged", "needs log", or last log time, but not work-log body text.
- **D-33:** Cards should avoid direct action clutter. Use card open behavior plus a more menu; status changes, work-log creation, blocker actions, and richer edits happen in the drawer.

### 工作日志写入体验

- **D-34:** Work logs are primarily written inside the task drawer.
- **D-35:** The full task detail page shows complete work-log history and deeper reading context.
- **D-36:** Work-log dates may be in the past or today, but not in the future.
- **D-37:** Backend validation and frontend date picker behavior should both reject future work-log dates.
- **D-38:** Commit hash, branch name, and repository URL fields are optional text fields for v1 manual/simulated code evidence.
- **D-39:** Phase 3 should save and display code-reference fields but must not call Git platforms or enforce strict Git-specific validation.
- **D-40:** Work-log creators may edit or soft-delete their own work logs for correction.
- **D-41:** Edited or deleted work logs must retain audit fields such as `updated_at` and `deleted_at`; records referenced by future acceptance evidence must not be physically deleted.

### the agent's Discretion

- Exact API route names, schema names, and component names may be selected during planning, as long as they follow existing FastAPI `/api/v1`, service-layer, Pinia, Vue Router, and Ant Design Vue patterns.
- The planner may choose the precise drawer layout and detail page section order, provided the drawer remains optimized for quick execution and the detail page remains the long-form context surface.
- The planner may decide whether to reserve hidden data fields for future 3-level subtasks, as long as Phase 3 UI exposes only one level and avoids recursive progress complexity.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### GSD Planning Baseline

- `.planning/PROJECT.md` — Project value, v1 boundaries, deferred scope, and evidence-gated MVP framing.
- `.planning/REQUIREMENTS.md` — Phase 3 requirements `TASK-01..08` and `WORK-01..06`, plus Phase 4/5 boundaries that Phase 3 must prepare for without implementing early.
- `.planning/ROADMAP.md` — Phase 3 goal, success criteria, notes, and explicit boundary that blockers are not task status.
- `.planning/STATE.md` — Current project state and workflow settings.
- `.planning/config.json` — GSD workflow configuration.
- `.planning/phases/01-auth-foundation/01-CONTEXT.md` — Prior foundation decisions for stack, auth shell, local services, and UI rules.
- `.planning/phases/02-team-project-board/02-CONTEXT.md` — Prior team/project/board decisions, especially fixed board columns and status mapping.
- `design-system/MASTER.md` — TTCS frontend visual source of truth; MUST guide all Phase 3 UI.

### Source Requirements and Design

- `01-requirements/02-srs.md` — SRS V2.4; task, work-log, blocker, status, and requirement traceability baseline.
- `01-requirements/05-change-request-001.md` — Work-log, multi-participant task, blocker notification, and Git-field reservation change request.
- `02-design/01-task-acceptance-design.md` — Evidence-gated acceptance model; Phase 3 must produce work-log, subtask, and blocker data that Phase 4 gates can trust.
- `02-design/02-high-level-design.md` — Module boundaries, task/work-log service responsibilities, permission table, and workflow diagrams.
- `02-design/03-low-level-design.md` — Detailed enums, data model sketches, services, status machine, frontend routes/components, and validation notes for tasks, work logs, blockers, and acceptance.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `backend/app/models/project.py` — Existing `Project`, `ProjectMember`, `BoardColumn`, `ProjectRole`, and `BoardColumnStatus` patterns. Phase 3 task status should align with the existing board-column status values.
- `backend/app/services/project_service.py` — Existing service-layer style, transaction usage, default board-column creation, and domain-specific error classes.
- `backend/app/services/permissions.py` — Existing team/project permission helpers. Phase 3 should extend this with task visibility/editing/participant/Owner checks.
- `backend/app/api/v1/projects.py` — Existing protected router and error mapping style for `/api/v1`.
- `frontend/src/views/ProjectBoardView.vue` — Existing board page that currently renders empty columns; Phase 3 should replace empty placeholders with real task cards and drawer behavior.
- `frontend/src/components/project/BoardColumn.vue` — Existing column visual structure and status accent pattern that task cards should integrate with.
- `frontend/src/stores/project.ts`, `frontend/src/api/projects.ts`, and `frontend/src/types/project.ts` — Existing Pinia/API/type organization to mirror for task APIs and stores.
- `frontend/src/layouts/AppLayout.vue` and `frontend/src/router/index.ts` — Existing app shell and protected-route structure for adding `/tasks/:taskId`.

### Established Patterns

- Backend code uses FastAPI routers, SQLAlchemy ORM models, Pydantic schemas, service classes, explicit permission helpers, and Alembic migrations.
- Protected endpoints depend on `get_current_user` and `get_db`.
- Frontend code uses Vue 3, TypeScript, Pinia, Vue Router, Axios, Ant Design Vue, lucide icons, and scoped component styles with semantic tokens.
- UI must avoid fake later-phase data and must follow the polished operational SaaS cockpit direction in `design-system/MASTER.md`.
- Phase 2 already fixed board columns as `TODO`, `IN_PROGRESS`, `IN_REVIEW`, `REJECTED`, and `DONE`; Phase 3 tasks must reuse this status model rather than invent custom board states.

### Integration Points

- Add task models and migrations alongside existing project/team/user models.
- Add task routers under `/api/v1`, likely with project-scoped list/create endpoints and task-scoped detail/work-log/subtask endpoints.
- Extend project board response or add task-list endpoints so board columns can render real tasks.
- Add task store/API/type modules in the frontend, mirroring existing project/team store patterns.
- Add task drawer and task detail route without exposing Phase 4 acceptance actions as completed features.
- Ensure work-log/blocker data created in Phase 3 is queryable by future acceptance gates, workbench queues, notifications, and reports.

</code_context>

<specifics>
## Specific Ideas

- The preferred user flow is: project board -> click task card -> editable drawer -> write log or mark blocker -> open full detail only for complex context.
- Task cards should make delivery risk visible at a glance, with blocker state taking visual priority over ordinary priority or date signals.
- Phase 3 should feel like a real execution cockpit, not a generic task-board clone.
- Work logs and blockers are not side notes; they are the evidence and risk trail that makes later acceptance meaningful.

</specifics>

<deferred>
## Deferred Ideas

- Full acceptance submission, gate result snapshots, Owner/project-manager Review, pass/reject/supplement evidence actions — Phase 4.
- Notification center, WebSocket push UI, personal workbench queues, and project reports — Phase 5, though Phase 3 should create the data they need.
- Real GitHub/GitLab integration and strict Git platform validation — v2; v1 uses manual/simulated code evidence fields.
- AI/Agent review and code-risk analysis — v2 only, never final completion authority.
- Three-level nested subtasks and recursive progress UI — deferred unless a later phase explicitly needs it.

</deferred>

---

*Phase: 3-任务执行、日志与阻塞闭环*
*Context gathered: 2026-05-18*
