---
status: testing
phase: 03-task-execution-log-blocker-loop
source:
  - 03-01-SUMMARY.md
  - 03-02-SUMMARY.md
  - 03-03-SUMMARY.md
  - 03-04-SUMMARY.md
started: 2026-05-18T16:58:34Z
updated: 2026-05-18T17:20:00Z
---

## Current Test

number: 4
name: Edit task basics in the drawer
expected: |
  Opening a task card shows the drawer with visible Chinese labels. Editing title, description, type, or priority saves through the API and refreshes both drawer/detail data and the board card where applicable.
awaiting: user response

## Tests

### 1. Phase 3 local demo starts with real seeded data
expected: After running the documented local setup, backend and frontend start successfully. The demo user can log in, open the project board, and see persisted Phase 3 task cards from backend seed data rather than frontend constants.
result: pass

### 2. Board shows API-backed task cards in fixed workflow columns
expected: The project board loads real task cards grouped by status column. Cards show title, type, priority, owner/participant signal, due date, subtask progress, and lightweight log/blocker state. No Phase 4 acceptance review, Phase 5 notification/report, real Git sync, or AI review controls are visible.
result: issue
reported: "截止日期无法设置，子任务进度怎么反馈完成，无法手动填写日志，没找到解除阻塞按钮，没有验收审核，通知，报表，ai  review功能接口"
severity: major

### 3. Create a task from the project board
expected: Creating a task from the board persists it through the API, adds it to the expected column, and opens or refreshes with the created task available for detail/drawer actions.
result: issue
reported: "点击创建任务，直接出现在代办栏了，还没有填写信息，保存任务也没有反应，点击创建任务，应该会有一个卡片弹出，填写信息确认后在成功创建啊"
severity: major

### 4. Edit task basics in the drawer
expected: Opening a task card shows the drawer with visible Chinese labels. Editing title, description, type, or priority saves through the API and refreshes both drawer/detail data and the board card where applicable.
result: [pending]

### 5. Add and complete one-level subtasks
expected: Adding a subtask displays it in the task drawer/detail checklist. Checking or unchecking it updates completed/total progress. The UI does not expose nested subtasks.
result: [pending]

### 6. Record a normal work log with optional code references
expected: The work-log form exposes visible fields for work date, hours, work type, content, and optional commit/branch/repository text. Future dates or invalid hours are rejected. A saved log appears in the task history without triggering any live Git integration.
result: [pending]

### 7. Mark a task blocked from a work log
expected: Marking a work log as blocking requires a blocker reason with at least 10 characters. After saving, the task card/detail shows the blocked state and current blocker summary.
result: [pending]

### 8. Resolve a blocker and preserve blocker history
expected: Resolving a blocker requires a resolution note with at least 10 characters. After all blockers are resolved, the task is no longer shown as blocked, and the blocker timeline/history keeps the resolution note.
result: [pending]

### 9. Open the protected direct task detail route
expected: Opening `/tasks/:taskId` while authenticated shows overview, subtasks, work-log history, blocker history, and a return path to the project board. Unauthenticated access redirects through the existing auth guard.
result: [pending]

## Summary

total: 9
passed: 1
issues: 2
pending: 6
skipped: 0
blocked: 0

## Gaps

- truth: "The project board loads real task cards grouped by status column. Cards show title, type, priority, owner/participant signal, due date, subtask progress, and lightweight log/blocker state. No Phase 4 acceptance review, Phase 5 notification/report, real Git sync, or AI review controls are visible."
  status: failed
  reason: "User reported: 截止日期无法设置，子任务进度怎么反馈完成，无法手动填写日志，没找到解除阻塞按钮，没有验收审核，通知，报表，ai  review功能接口"
  severity: major
  test: 2
  artifacts: []
  missing: []

- truth: "Creating a task from the board persists it through the API, adds it to the expected column, and opens or refreshes with the created task available for detail/drawer actions."
  status: failed
  reason: "User reported: 点击创建任务，直接出现在代办栏了，还没有填写信息，保存任务也没有反应，点击创建任务，应该会有一个卡片弹出，填写信息确认后在成功创建啊"
  severity: major
  test: 3
  artifacts: []
  missing: []
