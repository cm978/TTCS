---
status: diagnosed
phase: 02-team-project-board
source: [02-01-SUMMARY.md, 02-02-SUMMARY.md, 02-03-SUMMARY.md, 02-04-SUMMARY.md]
started: 2026-05-18T00:00:00+08:00
updated: 2026-05-18T10:59:00+08:00
---

## Current Test

[testing complete]

## Tests

### 1. Cold Start Smoke Test
expected: Kill any running backend/frontend service, start the application from scratch, open `/app` after login, and the team/project APIs load without server errors.
result: issue
reported: "Automated cold-start check hit GET /api/v1/teams -> 500 Internal Server Error; backend log shows sqlite3.OperationalError: no such table: teams"
severity: blocker

### 2. Authenticated Team/Project Start
expected: Open the app, register or log in, and land on `/app`. The page shows `团队与项目`, not the old Phase 1 `基础认证已就绪` copy. If the account has no teams, the primary empty state offers `创建第一个团队`.
result: pass

### 3. Create First Team
expected: Clicking `创建第一个团队` opens a `创建团队` form with visible name/description labels. Submitting a valid team creates the team, selects it, and exposes member management and project creation entry points.
result: pass

### 4. Invite And Accept Team Member
expected: From team member management, `邀请成员` opens an email/role form. A pending invitation appears as `待接受邀请`; when a user with that email logs in, `/app` shows `你有待接受的团队邀请` and accepting it joins the team with the invited role.
result: pass

### 5. Create Project And Open Board
expected: Creating a project from the selected team navigates directly to `/projects/:projectId/board`. The board shows the project title, member summary, `管理成员`, and five empty persisted columns: 待办, 进行中, 待验收, 打回修改, 已完成.
result: pass

### 6. Team Member Role Guards
expected: Team member management shows `管理员` and `成员` roles, supports role/removal actions for admins, and explains `团队至少需要保留 1 名管理员。` when the last admin cannot be demoted or removed.
result: pass

### 7. Project Member Drawer Guards
expected: On the project board, `管理成员` opens the `项目成员` drawer. It uses only `项目经理` and `项目成员`, shows `添加项目成员`, and explains `项目至少需要保留 1 名项目经理。` or `只有项目经理可以管理项目成员。` when edits are not allowed.
result: pass

## Summary

total: 7
passed: 6
issues: 1
pending: 0
skipped: 0
blocked: 0

## Gaps

- truth: "Cold start applies or requires Phase 2 schema before team/project APIs are used"
  status: failed
  reason: "Automated cold-start check hit GET /api/v1/teams -> 500 Internal Server Error; backend log shows sqlite3.OperationalError: no such table: teams"
  severity: blocker
  test: 1
  root_cause: "Local SQLite database backend/ttcs.db was still at Alembic revision 20260517_0001 with only the users table; Phase 2 migration 20260517_0002 had not been applied before starting the backend."
  artifacts:
    - path: "backend/ttcs.db"
      issue: "Runtime database missing teams, team_members, team_invitations, projects, project_members, and board_columns tables."
    - path: "backend/alembic/versions/20260517_0002_create_team_project_board.py"
      issue: "Migration exists but was not applied to the local runtime database."
  missing:
    - "Run `cd backend && uv run alembic upgrade head` before manual UAT, or add a documented/dev startup migration step."
  debug_session: ""
- truth: "Submitting the create-team form with a visible team name creates the team"
  status: resolved
  reason: "User reported: 无法创建团队，提示name is required,但是我已经输入团队名称了"
  severity: major
  test: 3
  root_cause: "CreateTeamModal uses Ant Design Vue form item names without binding the form model, so validation cannot read the reactive name field even though the input displays text."
  artifacts:
    - path: "frontend/src/components/team/CreateTeamModal.vue"
      issue: "a-form lacks :model binding and explicit rules for the reactive form object."
  missing:
    - "Bind a-form to the reactive form model and provide explicit validation rules for name/description."
  debug_session: ""
- truth: "Accepted invitations should not duplicate joined team members in the member management table"
  status: resolved
  reason: "User reported: 已经接受的，团队成员怎么还保留，这样一个成员的信息出现两次"
  severity: major
  test: 6
  root_cause: "TeamMemberTable renders every invitation returned by the team invitations API, including ACCEPTED records that are already represented by TeamMember rows."
  artifacts:
    - path: "frontend/src/components/team/TeamMemberTable.vue"
      issue: "Invitation rendering does not filter out accepted invitations."
  missing:
    - "Filter accepted invitations from the visible invitation rows while keeping pending/expired/cancelled invitation status rows."
  debug_session: ""
