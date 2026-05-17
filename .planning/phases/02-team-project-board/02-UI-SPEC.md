---
phase: 2
slug: team-project-board
status: approved
shadcn_initialized: false
preset: none
created: 2026-05-17
---

# Phase 2 — UI Design Contract

> Visual and interaction contract for Phase 2: 团队、项目与基础看板. Generated inline by Codex from `$gsd-ui-phase 2`, using `design-system/MASTER.md`, Phase 2 context/research, Phase 1 UI patterns, and `ui-ux-pro-max` guidance.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none |
| Preset | not applicable |
| Component library | Ant Design Vue 4.x, themed with TTCS project tokens |
| Icon library | `lucide-vue-next`; one consistent vector icon family |
| Font | `Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif` |

### Design Intent

Phase 2 turns the protected shell into the first real TTCS workspace. The UI must feel like a polished operational SaaS cockpit for small software teams: clear hierarchy, dense-but-readable management surfaces, real empty states, and explicit role/status affordances.

The interface should prove that teams, members, projects, roles, and board columns are real records. It must not fake tasks, work logs, acceptance data, reports, notifications, recent-project routing, Git evidence, or AI review.

### Required References

Downstream frontend planning and implementation MUST read:

- `design-system/MASTER.md` — project visual system and UI/UX rules.
- `.planning/phases/02-team-project-board/02-CONTEXT.md` — locked Phase 2 product and interaction decisions.
- `.planning/phases/02-team-project-board/02-RESEARCH.md` — technical research, frontend modules, validation strategy, and UI risks.
- `.planning/phases/01-auth-foundation/01-UI-SPEC.md` — Phase 1 typography, color, motion, auth/app shell continuity.
- `.planning/REQUIREMENTS.md` — Phase 2 `TEAM-01..03` and `PROJ-01..03`.
- `.planning/ROADMAP.md` — Phase 2 goal and success criteria.
- `/Users/moon/.codex/skills/ui-ux-pro-max/SKILL.md` — source UI/UX guidance.

`ui-ux-pro-max` search confirmed useful rules for this phase: tables need mobile handling, empty states need helpful next actions, active navigation must be visible, and view state should be deep-linkable. Its generated dark portfolio-style design recommendation is rejected for TTCS Phase 2 because this product needs a calm daily-use operational SaaS cockpit, not a portfolio/editorial visual system.

---

## Spacing Scale

Declared values (must be multiples of 4):

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Icon gaps, compact inline spacing |
| sm | 8px | Status chip gaps, table cell inner groups, compact form helper text |
| md | 16px | Default component padding, modal sections, form field stacks |
| lg | 24px | Page gutters, board column gaps, drawer body padding |
| xl | 32px | Desktop content group gaps, board header spacing |
| 2xl | 48px | Empty state panel spacing, major page section separation |
| 3xl | 64px | Wide desktop page rhythm only |

Exceptions: none.

### Layout Rules

- Minimum interactive target: 44px for buttons, icon buttons, row actions, drawer close buttons, and modal footer controls.
- Use 375px, 768px, 1024px, and 1440px as design/test breakpoints.
- No horizontal page scroll on mobile.
- Tables may use a contained horizontal scroll region on narrow screens, or collapse to stacked row cards. The page itself must not overflow.
- Board columns must use stable widths and responsive overflow. On desktop, show all five columns when practical; on narrow screens, use horizontal board scrolling inside the board region with visible column headings and no page-level overflow.
- Reserve layout space for loading states to avoid cumulative layout shift.

---

## Typography

| Role | Size | Weight | Line Height |
|------|------|--------|-------------|
| Body | 16px | 400 | 1.6 |
| Secondary body | 14px | 400 | 1.5 |
| Label | 14px | 500 | 1.4 |
| Compact label | 13px | 500 | 1.35 |
| Table text | 14px | 400 | 1.45 |
| Table header | 13px | 600 | 1.35 |
| Card title | 16px | 650 | 1.35 |
| Page heading | 24px | 650 | 1.25 |
| Workspace title | 28px | 700 | 1.2 |

### Typography Rules

- Body copy should never be below 13px.
- Form labels are always visible; placeholders cannot replace labels.
- Use tabular numbers for member counts, project counts, board column counts, dates, and duration/expiry values.
- Letter spacing must remain normal/default; no negative tracking.
- Chinese UI copy must remain short and direct.
- Long names and emails should wrap or truncate with tooltip/title; they must not force layout overflow.

---

## Color

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | `#F6F8FB` | App background and workspace canvas |
| Secondary (30%) | `#FFFFFF` / `#FDFEFE` | Main panels, management surfaces, drawers, board columns |
| Accent (10%) | `#2563EB` | Primary CTA, active nav, selected team/project, focus ring, key links |
| Destructive | `#DC2626` | Remove member, cancel invitation, destructive confirmations, errors |

Accent reserved for: create team, create project, accept invitation, active navigation, selected project/team, primary drawer/modal submit, keyboard focus ring, and key links.

### Semantic State Colors

| State | Token | Value | Usage |
|-------|-------|-------|-------|
| Neutral | `color-text-muted` / `color-border` | `#5B667A` / `#DDE4EF` | TODO/empty/default states |
| In Progress | `color-primary` | `#2563EB` | 进行中 board state |
| Review | `color-review` | `#7C3AED` | 待验收 board state |
| Rejected | `color-danger` | `#DC2626` | 打回修改 board state |
| Done | `color-success` | `#16A34A` | 已完成 board state |
| Warning | `color-warning` | `#D97706` | Expiring/expired invitation warnings |

### Color Rules

- Use semantic tokens, not raw hex values in component-local styles.
- Color must never be the only status indicator; pair color with text or an icon.
- Text contrast must be at least 4.5:1 for normal text.
- Do not use a dark portfolio/editorial palette for Phase 2.
- Avoid one-note dark blue/slate-only UI. Board state accents should use the semantic status tokens above.
- Do not use decorative gradient orbs, bokeh, or marketing hero gradients.

---

## Screens and Interaction Contracts

### `/app` Team/Project Start View

Purpose: replace the Phase 1 foundation page with a real entry point for teams and projects.

Required states:

- Loading state while fetching teams, projects, and pending invitations.
- No-team empty state with primary action `创建第一个团队`.
- Pending invitation state for the logged-in email, with accept action visible before or near team creation.
- Team/project selection state when the user has multiple teams or projects.
- Error state with retry action when team/project loading fails.

Required elements:

- Page heading: `团队与项目`.
- Short helper copy explaining that teams contain projects and projects contain the board workspace.
- Primary CTA for creating a team when no team exists.
- Project cards/list rows only for real projects returned by the API.
- Clear route targets for project board links, such as `/projects/:projectId/board`.

Must not include:

- Task counts.
- Work log counts.
- Acceptance review counts.
- Reports, charts, notifications, recent-project shortcuts, or fake activity feed.

### Team Creation Flow

Purpose: let authenticated users create teams and become team administrators.

Required elements:

- Modal or focused panel with visible labels for team name and description.
- Name helper: `2-50 个字符，团队名称需唯一`.
- Description helper: `最多 500 个字符`.
- Submit button loading/disabled state.
- Duplicate-name error near the form or as form-level error.
- Success path returns to `/app` or opens the team context with member management available.

Required copy:

- Primary CTA: `创建团队`
- Modal title: `创建团队`
- Success feedback: `团队已创建，你已成为团队管理员。`
- Error feedback: `创建团队失败。请检查团队名称后重试。`

### Team Member Management Page

Purpose: let team administrators view members, invite people, adjust roles, remove members, and handle pending invitations.

Required elements:

- Route such as `/teams/:teamId/members`.
- Table-oriented management surface.
- Columns: member/email, display name when available, team role, status, joined/invited time, and actions.
- Separate or grouped section for pending invitations.
- Invite action opens `InviteMemberModal`.
- Role selector supports only `TEAM_ADMIN` and `TEAM_MEMBER`.
- Remove member action uses destructive confirmation.
- Cancel invitation action uses destructive or warning confirmation.
- Disabled actions and explanatory text when removing/demoting would violate the final-admin rule.

Responsive contract:

- Desktop/tablet: use table.
- Narrow mobile: either wrap the table in a contained horizontal scroll region or render stacked row cards. The viewport must not horizontally scroll.

Required copy:

- Page heading: `团队成员`
- Invite CTA: `邀请成员`
- Role labels: `管理员`, `成员`
- Pending invitation label: `待接受邀请`
- Cancel invitation: `取消邀请`
- Remove member: `移除成员`
- Last admin guard: `团队至少需要保留 1 名管理员。`

### Invitation Acceptance

Purpose: make pending invitations discoverable for invited emails, including users who register after being invited.

Required elements:

- Pending invitation banner or list on `/app` for the logged-in user's email.
- Team name, inviter when available, invited role, and expiry date.
- Accept action.
- Expired/cancelled invitation states must be clearly labeled and not actionable.
- Loading and error states for accept action.

Required copy:

- Banner heading: `你有待接受的团队邀请`
- Accept CTA: `接受邀请`
- Expired state: `邀请已过期`
- Cancelled state: `邀请已取消`
- Accept success: `已加入团队。`

### Project Creation Flow

Purpose: let team members create a project and land directly in the board workspace.

Required elements:

- Create project action visible in team/project context for team members.
- Form with visible labels: project name, description, start date, end date.
- Name helper: `2-100 个字符`.
- Description helper: `最多 1000 个字符`.
- Date validation: end date must be later than start date.
- Submit loading/disabled state.
- On success, navigate directly to `/projects/:projectId/board`.

Required copy:

- Primary CTA: `创建项目`
- Modal title: `创建项目`
- Success feedback: `项目已创建，默认看板已就绪。`
- Date error: `结束日期必须晚于开始日期。`

### Project Board View

Purpose: show a real project workspace with persisted default board columns, member/role summary, and project member management entry.

Required elements:

- Route: `/projects/:projectId/board`.
- Header with project title, team name or breadcrumb, and member/role summary.
- Manage members action near the member summary.
- Five persisted board columns, in order:
  1. `待办` -> `TODO`
  2. `进行中` -> `IN_PROGRESS`
  3. `待验收` -> `IN_REVIEW`
  4. `打回修改` -> `REJECTED`
  5. `已完成` -> `DONE`
- Each column shows status label, semantic accent, empty state copy, and `0` count until Phase 3 tasks exist.
- No task cards, no sample tasks, and no create-task CTA in Phase 2.

Required empty-state copy:

- TODO: `暂无待办任务`
- IN_PROGRESS: `暂无进行中的任务`
- IN_REVIEW: `暂无待验收任务`
- REJECTED: `暂无打回修改任务`
- DONE: `暂无已完成任务`
- Shared body: `任务功能将在后续阶段接入。当前看板列已准备就绪。`

Forbidden content:

- Fake task titles.
- Task priority chips.
- Work log prompts.
- Acceptance buttons.
- Report widgets.
- Notification/activity feed.

### Project Member Drawer

Purpose: let project managers manage project members without leaving the board context.

Required elements:

- Drawer or modal launched from Project Board header.
- List existing project members with role labels.
- Add-member control selects from existing team members only.
- Role selector supports only `PROJECT_MANAGER` and `PROJECT_MEMBER`.
- Remove member action uses destructive confirmation.
- Disabled actions and explanatory text when removing/demoting would violate the final-project-manager rule.
- Non-project managers can view member summary but cannot edit; edit affordances are hidden or disabled with clear copy.

Required copy:

- Drawer title: `项目成员`
- Add CTA: `添加项目成员`
- Role labels: `项目经理`, `项目成员`
- Last manager guard: `项目至少需要保留 1 名项目经理。`
- Permission denial: `只有项目经理可以管理项目成员。`

---

## Copywriting Contract

| Element | Copy |
|---------|------|
| `/app` heading | 团队与项目 |
| No-team heading | 创建你的第一个团队 |
| No-team body | 团队用于组织成员和项目。创建团队后，你可以邀请成员并创建项目看板。 |
| Create team CTA | 创建团队 |
| Invite member CTA | 邀请成员 |
| Pending invitation heading | 你有待接受的团队邀请 |
| Accept invitation CTA | 接受邀请 |
| Team member page heading | 团队成员 |
| Create project CTA | 创建项目 |
| Project board empty body | 任务功能将在后续阶段接入。当前看板列已准备就绪。 |
| Manage project members CTA | 管理成员 |
| Project member drawer title | 项目成员 |
| Network error state | 请求失败。请检查本地服务是否启动，然后重试。 |
| Team duplicate error | 团队名称已存在，请换一个名称。 |
| Invitation duplicate error | 该邮箱已有待接受邀请。 |
| Last admin guard | 团队至少需要保留 1 名管理员。 |
| Last project manager guard | 项目至少需要保留 1 名项目经理。 |
| Destructive confirmation | 移除成员：移除后该成员将无法继续访问对应团队或项目。 |

### Copy Rules

- Use direct Chinese UI copy.
- Avoid technical implementation phrases such as `board_columns`, `JWT`, `Phase 3`, or enum names in visible UI.
- UI may say "后续接入" only in restrained empty states; do not turn pages into roadmap explanations.
- Error messages must include a recovery path.
- Destructive confirmations must name the exact action and consequence.

---

## Forms and Feedback

- Every input has a visible label and programmatic label association.
- Required fields are marked.
- Validate on blur or submit; avoid aggressive per-keystroke error flashing.
- Submit buttons show loading state and prevent duplicate submission.
- First invalid field receives focus after submit failure when practical.
- Async form errors use `aria-live="polite"` or equivalent where practical.
- Toasts may confirm success but must not be the only place an error appears.
- Role selectors must show current value before editing.
- Disabled controls need visible disabled state plus adjacent reason when the constraint is business-critical.

---

## Motion Contract

- Micro-interactions: 150-300ms.
- Use `transform` and `opacity`; do not animate width, height, top, or left.
- Respect `prefers-reduced-motion`.
- Required motion:
  - Button hover/press/focus feedback.
  - Modal/drawer open and close transition.
  - Form submit loading transition.
  - Empty-to-populated state transition for lists after API load.
  - Project creation success route transition, if already supported by app shell.
- Avoid decorative-only animation.
- Drawer and modal animations must remain interruptible and must not block keyboard interaction.

---

## Responsive Contract

| Viewport | Contract |
|----------|----------|
| 375px | Single-column `/app`; team/member forms full width; board scroll contained inside board region; no page horizontal scroll |
| 768px | Team/project selection can use two-column cards; member table may still use contained scroll |
| 1024px | Persistent app shell and board workspace; project member drawer can use 420-520px width |
| 1440px | Board and management surfaces use max-width/content rhythm to avoid stretched text |

### Responsive Rules

- Use `min-height: 100dvh` for app shell pages where full-height layout is needed.
- Do not disable zoom.
- Fixed/sticky nav must not obscure content.
- Table actions must remain reachable on mobile.
- Board column headers must remain visible when horizontally scrolling the board region.
- Avoid nested vertical scroll regions except for drawers/modals where the body scroll is expected.

---

## Component Contracts

### Navigation and App Shell

- Current route must be visibly active.
- Navigation items use icon + text, not emoji.
- Team/project routes must be deep-linkable.
- Logout/destructive actions stay visually separated from normal navigation.
- App shell must not show Phase 5 dashboard/report links as active data surfaces.

### Tables

- Team member table should use compact but readable row density.
- Row actions should be buttons or dropdown menu items with text labels.
- Icon-only row actions require `aria-label` and tooltip.
- Mobile handling must prevent viewport overflow.

### Modals and Drawers

- Modal/drawer title must identify the resource being edited.
- Escape and close button must dismiss when there are no unsaved changes.
- If unsaved changes exist, ask for confirmation before closing.
- Focus should move into the modal/drawer on open and return to the trigger on close when practical.

### Board Columns

- Board columns are purposeful repeated items, so card-like surfaces are allowed.
- Do not put cards inside cards.
- Each column has stable dimensions, status accent, label, and empty state.
- Column state color must include text label.

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | none | not required |
| third-party registries | none | not allowed in Phase 2 |

No shadcn or third-party UI registry components are used. Phase 2 should continue with Ant Design Vue 4.x plus TTCS tokens and local Vue components.

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS

**Approval:** approved 2026-05-17

## UI-SPEC VERIFIED
