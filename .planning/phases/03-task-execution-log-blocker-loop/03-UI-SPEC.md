---
phase: 03
slug: task-execution-log-blocker-loop
status: approved
shadcn_initialized: false
preset: ttcs-operational-cockpit
created: 2026-05-18
---

# Phase 03 — UI Design Contract

> Visual and interaction contract for Phase 3 frontend work. Generated for `任务执行、日志与阻塞闭环` and verified against `design-system/MASTER.md`, Phase 3 CONTEXT decisions, and existing Vue/Ant Design Vue patterns.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none |
| Preset | `ttcs-operational-cockpit` |
| Component library | Ant Design Vue 4.x |
| Icon library | `lucide-vue-next` |
| Font | `Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif` |

**Design intent:** Phase 3 must turn the existing empty project board into a real daily execution cockpit. Users should be able to scan task risk, open a task drawer, write a work log, mark or resolve blockers, and open `/tasks/:taskId` for deeper context without feeling they left the board workflow.

**Existing foundation to preserve:**

- Keep `AppLayout.vue` as the protected app shell.
- Keep `ProjectBoardView.vue` as the board page and extend it with task loading and drawer state.
- Keep `BoardColumn.vue` as the status-column surface, replacing empty-only content with real task cards and a scoped empty state.
- Use semantic tokens from `frontend/src/styles/tokens.css`; do not scatter raw hex values in new components except when adding project-level tokens.

---

## Required Screens and Surfaces

| Surface | Route / Component | Contract |
|---------|-------------------|----------|
| Project board | `/projects/:projectId/board`, `ProjectBoardView.vue` | Shows real tasks grouped under fixed Phase 2 columns. Board remains the primary execution workspace. |
| Board column | `BoardColumn.vue` | Displays column label, count, empty state, and task cards. Column accent follows status token mapping. |
| Task card | `TaskCard.vue` | Medium-density execution card: title, type, priority, Owner, participant count/avatars, due date, subtask progress, blocker signal, lightweight work-log state. |
| Task drawer | `TaskDrawer.vue` | Editable quick-action surface for basic fields, participants, status action, subtasks, work-log creation, blocker mark/resolve actions, and link to full detail. |
| Work-log form | `WorkLogForm.vue` | Visible labels for date, hours, work type, content, optional code fields, blocked checkbox, blocker reason. Future dates disabled. |
| Task detail page | `/tasks/:taskId`, `TaskDetailView.vue` | Full context page for subtasks, dependencies, full work-log history, blocker history, and future Phase 4 acceptance/evidence panels. |
| Subtask checklist | `SubtaskChecklist.vue` | One-level checklist only; shows objective progress from completed/total. |
| Blocker history | `BlockerTimeline.vue` or section within detail | Shows unresolved and resolved blocker records with reason, creator, time, resolver, resolution note. |

---

## Spacing Scale

Declared values must stay on the existing 4px rhythm.

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Icon gaps, chip internals, compact metadata spacing |
| sm | 8px | Card metadata gaps, tag groups, inline control gaps |
| md | 16px | Card padding, drawer section gaps, column inner gaps |
| lg | 24px | Board header padding, drawer body section padding, detail page section padding |
| xl | 32px | Detail page layout gaps, board-to-detail section gaps |
| 2xl | 48px | Major page breaks only |
| 3xl | 64px | Not used in Phase 3 app surfaces |

Exceptions: horizontal board scrolling may preserve existing `grid-template-columns: repeat(5, minmax(220px, 1fr))`; on mobile, columns may become horizontally scrollable lanes only if the board container is clearly labelled and page-level horizontal scroll is avoided.

---

## Typography

| Role | Size | Weight | Line Height |
|------|------|--------|-------------|
| Body | 16px | 400 | 1.5 |
| Secondary text | 14px | 400 | 1.5 |
| Label / chip | 13px | 600 | 1.3 |
| Card title | 15-16px | 650 | 1.35 |
| Column heading | 16px | 650 | 1.3 |
| Page heading | 28px | 700 | 1.2 |
| Drawer section heading | 16px | 650 | 1.3 |
| Detail section heading | 18px | 700 | 1.3 |

Rules:

- Do not scale font size with viewport width.
- Letter spacing stays `0`.
- Use tabular numbers for hours, counts, dates, and progress where feasible.
- Task-card metadata must wrap cleanly; long task titles clamp to 2 lines on cards and show full title in drawer/detail.

---

## Color

Use existing semantic tokens. Add new tokens only in `frontend/src/styles/tokens.css` if a repeated Phase 3 state cannot be expressed clearly with current tokens.

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | `var(--color-bg)` / `#F6F8FB` | App background and board page backdrop |
| Secondary (30%) | `var(--color-surface)` / `#FFFFFF` | Board header, columns, drawer, detail sections, task cards |
| Raised surface | `var(--color-surface-raised)` / `#FDFEFF` | Empty states, nested form sections, card metadata bands |
| Accent (10%) | `var(--color-primary)` / `#2563EB` | Primary actions, active navigation, focused links |
| Destructive | `var(--color-danger)` / `#DC2626` | Delete/soft-delete actions, rejected status, destructive confirmation |
| Blocker / warning | `var(--color-warning)` / `#D97706` | Blocker chips, unresolved blocker status, warning copy |
| Review | `var(--color-review)` / `#7C3AED` | `IN_REVIEW` column/status |
| Success | `var(--color-success)` / `#16A34A` | Completed subtask progress and resolved blocker state |

Accent reserved for: primary create/save actions, active route, active focus-visible treatment, and `IN_PROGRESS` status. Do not use primary blue for all icons or all chips.

Status mapping:

- `TODO`: muted neutral, pair with text `待办`.
- `IN_PROGRESS`: primary blue, pair with text `进行中`.
- `IN_REVIEW`: review violet, pair with text `待验收`; Phase 3 must not expose completed Review controls.
- `REJECTED`: danger red, pair with text `打回修改`.
- `DONE`: success green, pair with text `已完成`; Phase 3 must not allow direct participant completion.
- Blocked: warning amber with icon/text, never color alone; card blocker signal outranks priority and overdue styling.

---

## Interaction Contract

### Board and Card Behavior

- The project board remains visible after task-card interaction; clicking a task card opens `TaskDrawer`.
- Cards expose one clear open affordance plus a compact more menu. Do not place full action sets directly on cards.
- Task-card keyboard behavior:
  - Card open control is keyboard focusable.
  - More menu is a separate keyboard focus target with an accessible label.
  - Focus must move into the drawer when opened and return to the originating card when closed.
- Board columns show real task counts. Empty states remain per-column and must not describe implementation internals.

### Drawer Behavior

- Drawer title format: `{任务标题}` plus status/type chips.
- Drawer supports quick execution edits only:
  - title, description, type, priority, due date, labels
  - Owner/participants with 5-person limit messaging
  - status actions allowed in Phase 3
  - one-level subtasks and objective progress
  - work-log form
  - blocker mark/resolve controls
- Drawer includes a visible link/button: `打开完整详情`.
- If a user enters complex sections such as dependencies, full log history, or blocker history, drawer points to full detail instead of duplicating every table.
- Drawer must have loading, saving, disabled, success, and error states.

### Full Detail Page

- `/tasks/:taskId` is directly accessible and protected.
- Detail page includes project/board breadcrumb so users can return to the project board.
- Detail page prioritizes full history and structure:
  - task overview
  - subtasks
  - dependencies
  - participant history/current participants
  - complete work-log list
  - unresolved/resolved blocker history
  - reserved but disabled Phase 4 acceptance/evidence area only if needed; it must read as "not yet available" and not fake data.

### Work Log and Blocker Form Behavior

- Work-log form lives primarily in the drawer.
- Required visible labels:
  - 工作日期
  - 工时
  - 工作类型
  - 工作内容
  - 是否阻塞
  - 阻塞原因
  - Commit Hash（可选）
  - 分支名称（可选）
  - 仓库地址（可选）
- Work date picker disables future dates.
- Hours input uses numeric constraints: minimum `0.5`, maximum `24`, step `0.5`.
- When `是否阻塞` is checked, blocker reason becomes required and helper copy states `至少 10 个字符`.
- Resolve blocker action requires a visible resolution note field with helper copy `至少 10 个字符`.
- Code fields are optional plain text and must not imply live Git synchronization.

---

## Copywriting Contract

| Element | Copy |
|---------|------|
| Primary CTA | `创建任务` |
| Secondary CTA | `记录工作日志` |
| Drawer detail link | `打开完整详情` |
| Empty state heading | `暂无任务` |
| Empty state body | `当前列还没有真实任务。创建任务后，它会按状态出现在这里。` |
| Board loading | `正在加载项目任务…` |
| Board error | `项目任务加载失败，请稍后重试。` |
| Task save error | `任务保存失败，请检查字段后重试。` |
| Participant limit helper | `每个任务最多 5 名参与者，Owner 会自动计入。` |
| Work-log empty heading | `还没有工作日志` |
| Work-log empty body | `记录今天的进展，让后续验收有据可查。` |
| Blocker chip | `阻塞中` |
| Blocker helper | `存在未解除阻塞时，任务后续不能提交验收。` |
| Resolve blocker CTA | `解除阻塞` |
| Destructive confirmation | `删除任务：任务将被软删除，历史日志和阻塞记录不会被物理删除。` |
| Soft-delete log confirmation | `删除工作日志：日志会被标记删除，历史审计信息会保留。` |

Copy rules:

- Use Chinese-first product copy.
- Do not use implementation phrases like "Phase 3" in visible app copy.
- Do not show fake report, notification, acceptance, Git sync, or AI review copy as if implemented.
- Empty states should guide the next real action, not describe future engineering work.

---

## Layout Contract

### Desktop

- Keep board content within the existing `ProjectBoardView` max-width rhythm unless task density requires widening to `1280px`.
- Board header remains a single operational header: project name, member summary, and primary create-task action.
- Board columns retain fixed status order: `TODO`, `IN_PROGRESS`, `IN_REVIEW`, `REJECTED`, `DONE`.
- Task cards use stable card width inside each column and must not resize column width based on content.
- Drawer width target: `560px` for task editing; may use `640px` when work-log form and subtask panel are both visible.
- Detail page uses a two-zone layout:
  - main column for task overview, subtasks, logs
  - side panel for Owner, participants, status, due date, blocker summary

### Tablet and Mobile

- Header stacks cleanly below `900px`.
- Board may use horizontal lane scrolling, but app shell/page must avoid accidental full-page horizontal scroll.
- Task cards remain at least `220px` wide in lanes.
- Drawer width becomes full viewport on small screens.
- Detail page collapses side panel below main content.
- All interactive controls keep at least 44px touch target where practical.

---

## Component Contracts

### `TaskCard.vue`

Required states:

- default
- hover
- keyboard focus
- selected/open
- blocked
- overdue
- loading skeleton
- disabled/permission-limited

Required visible data:

- title
- task type
- priority
- Owner
- participants count or avatars
- due date
- subtask progress as `已完成/总数`
- blocker signal, if unresolved blocker exists
- lightweight log state, such as `今日已写日志` or `待写日志`

Do not show:

- full work-log content
- full dependency list
- acceptance gate results
- AI/Git sync status

### `TaskDrawer.vue`

Required states:

- loading detail
- edit ready
- saving
- validation errors
- permission-limited read-only sections
- blocker unresolved
- blocker resolved

Required actions:

- save task basics
- update participants if current user is Owner or project manager
- add/check subtasks
- write work log
- mark blocker through work log
- resolve blocker if permitted
- open full detail page

### `TaskDetailView.vue`

Required states:

- loading
- not found / no access
- detail loaded
- work-log history empty
- blocker history empty

Required navigation:

- breadcrumb to project board
- direct route `/tasks/:taskId`
- protected route behavior aligned with existing router guard

### `WorkLogForm.vue`

Required states:

- pristine
- dirty
- submitting
- validation errors
- submit success
- submit failure
- blocked toggle on/off

Validation copy must be visible near the relevant field.

---

## Accessibility Contract

- Every input has a visible label.
- Icon-only controls require `aria-label`; unfamiliar icon-only controls require tooltip text.
- Do not rely on color alone for status; status chips include text and, where useful, lucide icon.
- Drawer focus trap follows Ant Design Vue behavior; implementation must return focus to originating card after close.
- Form errors appear near fields and are announced through accessible Ant Design Vue form/alert patterns where feasible.
- Task cards must be reachable by keyboard without requiring pointer hover.
- Blocker chip contrast must meet 4.5:1 for text, or use darker text on light amber background.
- Destructive actions are separated from primary task actions and require confirmation.

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | none | not required |
| third-party registries | none | not allowed for Phase 3 |

No third-party UI block registry should be introduced. Use Ant Design Vue, existing scoped components, `lucide-vue-next`, and TTCS semantic tokens.

---

## Implementation Boundaries

Allowed in Phase 3 UI:

- Real persisted tasks on the project board.
- Task drawer and detail route.
- Work-log creation/edit/soft-delete UI.
- Blocker mark/resolve UI.
- One-level subtask checklist and objective progress display.
- Dependency display/edit UI for same-project dependencies if backend support exists in the plan.

Not allowed in Phase 3 UI:

- Fake notification center.
- Fake personal workbench queues.
- Fake reports or charts.
- Acceptance Review pass/reject actions.
- Real Git sync status.
- AI/Agent review panels.
- Three-level nested subtask UI.
- Board column customization.

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS — concrete Chinese-first copy, action-oriented empty/error states, no fake future features.
- [x] Dimension 2 Visuals: PASS — operational cockpit surfaces, medium-density task cards, drawer/detail split, no decorative hero/orb patterns.
- [x] Dimension 3 Color: PASS — semantic tokens and explicit status mapping; blocker signal uses warning token plus text.
- [x] Dimension 4 Typography: PASS — stable sizes, readable Chinese support, no viewport-scaled type or negative letter spacing.
- [x] Dimension 5 Spacing: PASS — 4px rhythm, stable card/column/drawer dimensions, responsive constraints.
- [x] Dimension 6 Registry Safety: PASS — no shadcn or third-party registry dependency introduced.

**Approval:** approved 2026-05-18
