---
phase: 1
slug: auth-foundation
status: approved
shadcn_initialized: false
preset: none
created: 2026-05-17
---

# Phase 1 — UI Design Contract

> Visual and interaction contract for Phase 1: 应用基础与认证骨架. Generated inline by Codex from `$gsd-ui-phase 1`, using `design-system/MASTER.md`, Phase 1 context, and `ui-ux-pro-max` guidance.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none |
| Preset | not applicable |
| Component library | Ant Design Vue 4.x, themed with TTCS project tokens |
| Icon library | `lucide-vue-next` preferred; one consistent vector icon family |
| Font | `Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif` |

### Design Intent

Phase 1 UI must feel like a polished operational SaaS foundation, not a generic scaffold page. The auth screens and protected app shell should signal TTCS's product themes: delivery evidence, blocker visibility, human review, and task acceptance. It must not fake Phase 2/3/5 data.

### Required References

Downstream frontend planning and implementation MUST read:

- `design-system/MASTER.md` — project visual system and UI/UX rules.
- `.planning/phases/01-auth-foundation/01-CONTEXT.md` — locked Phase 1 product and UI decisions.
- `.planning/REQUIREMENTS.md` — Phase 1 `AUTH-01..04`, `ARCH-01..04`.
- `.planning/ROADMAP.md` — Phase 1 success criteria.
- `/Users/moon/.codex/skills/ui-ux-pro-max/SKILL.md` — source UI/UX guidance.

`ui-ux-pro-max` script check was run successfully after repair. The generated design-system recommendation is useful for pattern/style validation, but its red color recommendation is not adopted because TTCS needs a calmer task-collaboration SaaS palette with semantic status colors.

---

## Spacing Scale

Declared values (must be multiples of 4):

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Icon gaps, compact inline spacing |
| sm | 8px | Field helper text gaps, compact stack spacing |
| md | 16px | Default component padding and form spacing |
| lg | 24px | Auth panel padding, shell content gutters on mobile/tablet |
| xl | 32px | Desktop content gutters, major card spacing |
| 2xl | 48px | Auth screen split layout gap, page-level spacing |
| 3xl | 64px | Large desktop auth composition spacing |

Exceptions: none.

### Layout Rules

- Minimum interactive target: 44px.
- Use 375px, 768px, 1024px, and 1440px as design/test breakpoints.
- No horizontal scroll on mobile.
- App shell sidebar/topbar dimensions must be stable and must not shift while loading current user.
- Reserve space for loading states to avoid cumulative layout shift.

---

## Typography

| Role | Size | Weight | Line Height |
|------|------|--------|-------------|
| Body | 16px | 400 | 1.6 |
| Secondary body | 14px | 400 | 1.5 |
| Label | 14px | 500 | 1.4 |
| Compact label | 13px | 500 | 1.35 |
| Heading | 24px | 650 | 1.25 |
| Display | 32px | 700 | 1.15 |

### Typography Rules

- Body copy should never be below 13px.
- Form labels are always visible; placeholders cannot replace labels.
- Use tabular numbers for metrics, timers, counts, and version/status details.
- Letter spacing must remain normal/default; no negative tracking.
- Chinese text must remain legible with system CJK fonts.

---

## Color

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | `#F6F8FB` | App background and page canvas |
| Secondary (30%) | `#FFFFFF` / `#FDFEFE` | Auth panels, app shell surfaces, raised content panels |
| Accent (10%) | `#2563EB` | Primary CTA, active nav, focus ring, key links |
| Destructive | `#DC2626` | Logout confirmation errors, destructive/error states only |

Accent reserved for: primary auth submit, active route indicator, keyboard focus ring, current-user/protected-session highlight, key links.

### Semantic State Colors

| State | Token | Value | Usage |
|-------|-------|-------|-------|
| Success | `color-success` | `#16A34A` | Login/register success, approved status later |
| Warning | `color-warning` | `#D97706` | Blocker/warning status later |
| Danger | `color-danger` | `#DC2626` | Form errors, rejected/destructive states |
| Review | `color-review` | `#7C3AED` | Acceptance/review status later |
| Accent | `color-accent` | `#14B8A6` | Secondary progress/status accents |

### Color Rules

- Use semantic tokens, not raw hex values in component-local styles.
- Color must never be the only status indicator; pair color with text or icon.
- Text contrast must be at least 4.5:1 for normal text.
- Do not adopt `ui-ux-pro-max` generated red-primary palette for TTCS Phase 1; it reads too aggressive for a daily-use collaboration product.
- Avoid one-note dark blue/slate-only UI. Use semantic accents for review, blocker, success, and danger states.

---

## Screens and Interaction Contracts

### Login Screen

Purpose: let existing users authenticate and enter the protected TTCS shell.

Required elements:

- TTCS product identity.
- Email field with visible label.
- Password field with visible label.
- Submit button with loading/disabled state.
- Link or switch action to registration.
- Inline field errors.
- Auth-level error summary for invalid credentials or network failure.
- Product signal panel or visual area that communicates "evidence -> review -> complete" without fake task data.

Must not include:

- Forgot password link or password reset placeholder.
- Email verification prompt.
- Fake teams, projects, tasks, dashboards, or acceptance records.

### Register Screen

Purpose: create the first user account for local/demo use.

Required elements:

- Name or display name if backend supports it; otherwise email and password only.
- Email field with visible label.
- Password field with visible label and basic requirement helper text.
- Confirm password if implementation uses it.
- Submit button with loading/disabled state.
- Link or switch action to login.
- Inline validation and clear recovery text.

Must not include:

- Real email delivery or verification UX.
- Password reset flow.

### Protected App Shell

Purpose: prove authenticated access and provide reusable shell for later phases.

Required elements:

- TTCS identity in topbar or sidebar.
- Current user affordance showing email/display name.
- Logout action visually separated from normal nav.
- Responsive navigation shell.
- Main content region with Phase 1 foundation status and current user information.
- Clear protected-route behavior: unauthenticated users are redirected to login.

Allowed placeholder content:

- "基础认证已就绪" / "Authentication foundation ready".
- Current user details from `/me`.
- Small static explanation of Phase 1 capabilities.

Forbidden placeholder content:

- Real workspace queues.
- Project/task counts.
- Team/project/task creation shortcuts.
- Acceptance gate or dashboard metrics.

---

## Copywriting Contract

| Element | Copy |
|---------|------|
| Primary CTA | 登录 TTCS |
| Register CTA | 创建账号 |
| Logout action | 退出登录 |
| Protected empty state heading | 基础认证已就绪 |
| Protected empty state body | 你已进入受保护的 TTCS 应用壳。团队、项目和任务能力将在后续阶段接入。 |
| Login error state | 登录失败。请检查邮箱和密码后重试。 |
| Register error state | 创建账号失败。请检查表单信息后重试。 |
| Network error state | 请求失败。请检查本地服务是否启动，然后重试。 |
| Destructive confirmation | 退出登录：退出后需要重新登录才能访问受保护页面。 |

### Copy Rules

- Use short, direct Chinese UI copy.
- Avoid internal implementation phrases in user-facing UI.
- Error messages must include a recovery path.
- Do not expose stack traces, raw backend errors, tokens, or secrets.

---

## Forms and Feedback

- Every input has a visible label and programmatic label association.
- Password fields should include show/hide toggle if low implementation cost.
- Validate on blur or submit; avoid aggressive per-keystroke error flashing.
- Submit buttons show loading state and prevent duplicate submission.
- First invalid field receives focus after submit failure when practical.
- Use `aria-live="polite"` or equivalent for async auth errors when practical.
- Toasts must not steal focus.

---

## Motion Contract

- Micro-interactions: 150-300ms.
- Use `transform` and `opacity`; do not animate layout properties.
- Respect `prefers-reduced-motion`.
- Required motion:
  - Button press/hover/focus feedback.
  - Auth form submit loading transition.
  - Login/register panel switch or route transition, if implemented.
  - App shell content fade/slide-in after auth.
- Avoid decorative-only animation.

---

## Responsive Contract

| Viewport | Contract |
|----------|----------|
| 375px | Single-column auth layout, full-width form panel, no horizontal scroll |
| 768px | Auth form and product signal may split if space allows |
| 1024px | App shell may use persistent sidebar/topbar |
| 1440px | Content max width and shell spacing should prevent over-stretched text |

### Responsive Rules

- Use `min-height: 100dvh` for full-height auth/app screens.
- Do not disable zoom.
- Auth form remains usable in mobile landscape.
- Fixed/sticky nav must not obscure content.

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | none | not required |
| third-party blocks | none | prohibited unless explicitly reviewed |
| Ant Design Vue | Form, Input, Button, Layout, Menu, Alert/Message, Spin/Skeleton as needed | Theme/wrap with TTCS tokens; do not accept generic default styling everywhere |

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS

**Approval:** approved 2026-05-17

### Verification Notes

- Copywriting is specific to Phase 1 and avoids future feature promises.
- Visual direction follows `design-system/MASTER.md` and strengthens TTCS identity.
- Color system uses semantic tokens and rejects the unsuitable red-primary script recommendation.
- Typography remains performant and Chinese-friendly.
- Spacing uses multiples of 4 and aligns with `ui-ux-pro-max`.
- Registry safety is clear: no shadcn, no third-party block imports, Ant Design Vue must be themed.
