# Phase 2: 团队、项目与基础看板 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-17
**Phase:** 2-团队、项目与基础看板
**Areas discussed:** 团队邀请形态, 团队角色与项目角色边界, 项目创建后的默认入口, 基础看板的真实程度, 成员管理体验

---

## 团队邀请形态

| Option | Description | Selected |
|--------|-------------|----------|
| 演示优先邮箱直邀 | 管理员输入邮箱和角色，系统创建待接受邀请记录；暂不发真实邮件。 | ✓ |
| 直接添加已注册用户 | 只能把系统里已有账号加入团队。 | |
| 完整邮件邀请 | 生成邀请链接、发送邮件、处理过期和重复邀请。 | |

**User's choice:** 1
**Notes:** User selected demo-first email invitation. Follow-up decisions: unregistered emails may be invited; after registration the user should be able to accept matching pending invitations; invited role takes effect on acceptance; invitation states are `PENDING`, `ACCEPTED`, `EXPIRED`, and `CANCELLED`; pending invitations expire after 7 days; administrators can cancel pending invitations.

---

## 团队角色与项目角色边界

| Option | Description | Selected |
|--------|-------------|----------|
| 两档团队角色：管理员 / 成员 | Covers current SRS without introducing owner-transfer complexity. | ✓ |
| 三档团队角色：拥有者 / 管理员 / 成员 | More SaaS-like, but adds owner transfer and final-owner rules. | |
| 先不区分团队角色 | Lightweight but too weak for member management. | |

**User's choice:** 1
**Notes:** Team roles are `TEAM_ADMIN` and `TEAM_MEMBER`.

| Option | Description | Selected |
|--------|-------------|----------|
| 项目经理 / 项目成员两档 | Project creator becomes project manager; detailed roles deferred. | ✓ |
| 项目经理 / 技术负责人 / 开发 / 测试 | Closer to the full HLD role table, but Phase 2 lacks behavior differences. | |
| 不做项目角色 | Too weak for project member management and later review authority. | |

**User's choice:** 1
**Notes:** Project roles are `PROJECT_MANAGER` and `PROJECT_MEMBER`.

| Option | Description | Selected |
|--------|-------------|----------|
| 团队管理员不自动拥有项目权限 | Cleanest role boundary. | |
| 团队管理员默认可管理所有项目 | Convenient but over-broad. | |
| 团队管理员可查看所有项目，但修改项目仍需项目经理身份 | Preserves visibility while keeping project edit authority scoped. | ✓ |

**User's choice:** 3
**Notes:** Team administrators may view projects under the team, but project edits/member role changes require project-manager authority.

| Option | Description | Selected |
|--------|-------------|----------|
| 只能从团队成员中加入项目 | Keeps project membership under team membership. | ✓ |
| 项目经理直接邀请邮箱进项目，并顺带加入团队 | Faster UX, but mixes team and project invitation concepts. | |
| 允许项目成员不属于团队 | Flexible but breaks team/project hierarchy. | |

**User's choice:** 1
**Notes:** Project members must be existing team members.

---

## 项目创建后的默认入口

| Option | Description | Selected |
|--------|-------------|----------|
| 直接进入项目看板页 | Best matches the roadmap goal of entering a default board workspace. | ✓ |
| 进入项目概览页 | Gentler, but weakens the board-workspace value. | |
| 停留在项目列表并显示成功反馈 | Simpler, but less direct for demo flow. | |

**User's choice:** 1
**Notes:** After project creation, navigate directly to the new board page.

| Option | Description | Selected |
|--------|-------------|----------|
| 引导式空状态：创建第一个团队 | Turns `/app` into the real Phase 2 starting point. | ✓ |
| 项目列表页为空状态 | Works, but underplays the team structure. | |
| 保留 Phase 1 基础页，再加入口按钮 | Minimal change but weaker product feel. | |

**User's choice:** 1
**Notes:** `/app` should guide users with no teams toward creating their first team.

| Option | Description | Selected |
|--------|-------------|----------|
| 进入上次访问的项目；没有记录则进入最近创建项目 | Natural UX, but requires recent project state. | |
| 始终进入团队/项目选择页 | Clearer and avoids recent-project routing in Phase 2. | ✓ |
| 始终进入最新创建的项目 | Simple but can surprise users. | |

**User's choice:** 2
**Notes:** With multiple teams/projects, default to a team/project selection page.

| Option | Description | Selected |
|--------|-------------|----------|
| 项目标题 + 成员/角色摘要 + 看板列 | Shows that project membership is real without faking reports/tasks. | ✓ |
| 纯看板视图，只展示默认列 | Focused but weakens management affordances. | |
| 项目配置页 + 看板预览 | Management-heavy for this phase. | |

**User's choice:** 1
**Notes:** Board page header should include project title and member/role summary.

---

## 基础看板的真实程度

| Option | Description | Selected |
|--------|-------------|----------|
| 不允许自定义，只自动创建固定默认列 | Matches roadmap note and fixed task-state direction. | ✓ |
| 允许重命名/排序默认列 | Adds flexibility but complicates state mapping. | |
| 允许新增/删除列 | Out of phase and conflicts with fixed status machine. | |

**User's choice:** 1
**Notes:** Board columns are fixed in Phase 2.

| Option | Description | Selected |
|--------|-------------|----------|
| 真实空状态，不放假任务卡 | Avoids fake Phase 3 task data. | ✓ |
| 放演示占位卡，但明确标记为示例 | Richer visually but violates no-fake-data direction. | |
| 只显示列标题，列体为空 | Clean but can look unfinished. | |

**User's choice:** 1
**Notes:** Empty columns should show real empty states, not sample cards.

| Option | Description | Selected |
|--------|-------------|----------|
| 持久化为真实列记录 | Creates `board_columns` in the project transaction for later task references. | ✓ |
| 前端根据项目状态硬编码展示列 | Lightweight but causes later migration/refactor. | |
| 后端返回枚举，前端临时渲染 | Partial structure but weaker for ordering and future references. | |

**User's choice:** 1
**Notes:** Default columns must be real persisted records.

| Option | Description | Selected |
|--------|-------------|----------|
| 一列对应一个固定任务状态 | Best supports Phase 3/4 status machine. | ✓ |
| 列只是展示容器，任务状态单独维护 | More flexible but too complex now. | |
| Phase 2 暂不定义状态关系 | Lightweight but likely causes Phase 3 rework. | |

**User's choice:** 1
**Notes:** Default columns map one-to-one to `TODO`, `IN_PROGRESS`, `IN_REVIEW`, `REJECTED`, and `DONE`.

---

## 成员管理体验

| Option | Description | Selected |
|--------|-------------|----------|
| 表格型管理台 | Dense and appropriate for administrator operations. | ✓ |
| 成员卡片墙 | Friendlier but lower management density. | |
| 轻量列表 + 右侧详情抽屉 | Good UX but heavier for Phase 2. | |

**User's choice:** 1
**Notes:** Team member management should be table-oriented.

| Option | Description | Selected |
|--------|-------------|----------|
| 放在项目看板页顶部/侧边的成员管理入口 | Keeps project member management in project context. | ✓ |
| 放在独立“项目设置”页面 | Clear but adds page weight. | |
| 放在团队成员页里按项目筛选 | Centralized but weakens project-manager context. | |

**User's choice:** 1
**Notes:** Project member management should be reachable from the board page.

| Option | Description | Selected |
|--------|-------------|----------|
| 抽屉/弹窗式成员管理 | Keeps board context while managing project members. | ✓ |
| 独立页面式项目成员管理 | Better for complex permissions, too heavy now. | |
| 直接在看板页内联编辑成员列表 | Fast but can clutter the board and mobile layout. | |

**User's choice:** 1
**Notes:** Use drawer/modal project member management.

| Option | Description | Selected |
|--------|-------------|----------|
| 保留最小管理员/经理约束 | Prevents teams/projects from becoming unmanageable. | ✓ |
| 只限制团队至少 1 个管理员，项目经理不限制 | Simpler but can orphan projects. | |
| Phase 2 只做提示，不做硬限制 | Too weak; backend data can enter bad states. | |

**User's choice:** 1
**Notes:** Backend must enforce at least one team administrator and one project manager, including self-removal edge cases.

## the agent's Discretion

- Exact API route names, schema names, service decomposition, and frontend component names.
- Exact invitation acceptance UI placement, provided pending invitations are discoverable for the logged-in email.
- Exact table columns and drawer layout, provided the interface follows the TTCS design system and does not fake later-phase data.

## Deferred Ideas

- Real email delivery and invitation links.
- Project-level invitation of team-external users.
- Detailed project roles such as technical lead, developer, and tester.
- Recent-project routing.
- Board column customization.
- Task cards, work logs, blockers, acceptance, notifications, reports, and activity feeds.
