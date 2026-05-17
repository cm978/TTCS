# TTCS Design System

**Source:** `ui-ux-pro-max` skill guidance, adapted for TTCS  
**Created:** 2026-05-17  
**Applies to:** TTCS frontend, especially Vue 3 + Ant Design Vue screens

## Design Intent

TTCS should feel like a polished operational SaaS product for small software teams: clear, efficient, trustworthy, and visually richer than a plain admin panel. The interface should communicate "delivery evidence and task acceptance" through structured surfaces, strong hierarchy, traceable status states, and purposeful motion.

This is not a marketing landing page and not a decorative dashboard. The first screen after login should be the usable app shell. Visual quality comes from layout rhythm, semantic color, refined surfaces, meaningful empty states, and clear interaction feedback.

## Product Fit

- **Product type:** Productivity SaaS / task collaboration / project operations.
- **Audience:** Small software teams, project managers, technical leads, developers, testers.
- **Primary work mode:** Repeated daily use, scanning queues, checking status, submitting and reviewing work.
- **Design posture:** Professional, dense enough for work, but with enough visual identity to avoid feeling like a generic template.

## Visual Style

- Use a **modern operational cockpit** style: clean panels, compact spacing, strong status chips, clear section rhythm, and subtle depth.
- Prefer **soft elevation and crisp borders** over heavy shadows.
- Use **subtle glass/surface effects only where they clarify hierarchy**, such as auth panels or sticky navigation. Do not use blur as decoration.
- Avoid decorative gradient orbs, bokeh blobs, emoji icons, and random illustrative flourishes.
- Cards must be purposeful: auth panel, repeated task/project items, modals, and framed tools. Do not put cards inside cards.

## Color System

Use semantic tokens rather than raw hex values inside components.

### Core Tokens

| Token | Suggested value | Use |
|-------|-----------------|-----|
| `color-bg` | `#F6F8FB` | App background |
| `color-surface` | `#FFFFFF` | Main surfaces and panels |
| `color-surface-raised` | `#FDFEFE` | Elevated panels |
| `color-text` | `#172033` | Primary text |
| `color-text-muted` | `#5B667A` | Secondary text |
| `color-border` | `#DDE4EF` | Borders/dividers |
| `color-primary` | `#2563EB` | Primary actions and active nav |
| `color-primary-strong` | `#1D4ED8` | Hover/pressed primary |
| `color-accent` | `#14B8A6` | Positive progress and secondary accent |
| `color-warning` | `#D97706` | Blocker/warning states |
| `color-danger` | `#DC2626` | Destructive/error states |
| `color-success` | `#16A34A` | Approved/success states |
| `color-review` | `#7C3AED` | Review/acceptance state accent |

### State Semantics

- **待办:** muted neutral.
- **进行中:** primary blue.
- **待验收:** review violet.
- **打回修改:** danger red.
- **已完成:** success green.
- **阻塞:** warning amber with icon/text; never use color alone.

## Typography

- Use system UI fonts by default for performance and Chinese support:
  `Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif`.
- Body text starts at 16px where possible; compact UI labels may use 13-14px if contrast and readability remain strong.
- Line height:
  - Body: 1.5-1.7
  - Labels/buttons: 1.2-1.4
  - Dense tables/cards: keep legible, never below 12px.
- Use tabular numbers for metrics, durations, counts, and time values.
- Do not use negative letter spacing.

## Layout Rhythm

- Use an 8px spacing rhythm with 4px increments for fine adjustments.
- Breakpoints:
  - 375px: small phone
  - 768px: tablet
  - 1024px: app shell/sidebar breakpoint
  - 1440px: wide desktop
- Avoid horizontal scroll on mobile.
- Use stable dimensions for nav, toolbar, status chips, icon buttons, and auth panels.
- Prefer desktop app shell with sidebar/topbar; on mobile, collapse navigation predictably.
- Reserve space for loading and async content to prevent layout shift.

## Component Standards

### Buttons

- One primary action per surface.
- Buttons must show hover, focus, pressed, disabled, loading, success/error states.
- Icon-only buttons need accessible labels and visible tooltips when meaning is not obvious.
- Minimum interactive target: 44px.

### Forms

- Use visible labels, not placeholder-only labels.
- Show validation near the field.
- Validate on blur or submit, not aggressively on every keystroke.
- Submit buttons show loading state and prevent duplicate submission.
- Password fields should support show/hide if implementation cost is small.

### Navigation

- Current route must be clearly highlighted.
- Navigation items should include icon + text.
- Logout/destructive actions must be separated from normal navigation.
- Route changes should keep keyboard focus and screen reader order sensible.

### Empty and Loading States

- Use skeletons for loading longer than 300ms.
- Empty states should explain what exists now and what comes later, without describing implementation internals.
- Phase 1 protected home may show "基础认证已就绪" style content, but must not fake teams/projects/tasks.

## Motion

- Micro-interactions: 150-300ms.
- Use transform and opacity, not width/height/top/left animations.
- Respect `prefers-reduced-motion`.
- Motion must communicate state changes: login success, route transition, button press, panel reveal.
- Avoid decorative-only animation.

## Accessibility Requirements

- Text contrast: 4.5:1 minimum for normal text.
- Do not remove focus rings.
- Every input has a label.
- Every icon-only action has `aria-label`.
- Keyboard navigation must follow visual order.
- Do not rely on color alone; pair status colors with icon/text.
- Toasts/errors should be announced with appropriate live regions where feasible.

## Phase 1 UI Direction

Phase 1 should produce a visually polished foundation without pretending the rest of the product exists.

### Auth Screens

- Login/register should feel branded and product-specific.
- Use a focused auth panel plus a restrained product signal area showing TTCS themes: evidence, review, blockers, delivery loop.
- Do not include real team/project/task data.
- Use crisp labels, clear errors, loading feedback, and success feedback.

### Protected App Shell

- After login, show a reusable `AppLayout` with:
  - Topbar or header with TTCS identity and current user menu.
  - Sidebar/navigation area with future destinations visible only as disabled or clearly unavailable if needed.
  - Main content region showing Phase 1 foundation status and current user info.
  - Logout action.
- The shell should be ready for Phase 2 team/project pages and Phase 3 task pages.

## Implementation Notes

- Use Ant Design Vue components where they help speed and consistency, but wrap them with project-level tokens/styles instead of accepting default generic styling everywhere.
- Prefer a single icon family such as `lucide-vue-next` if icons are needed.
- Define CSS variables or theme tokens early.
- Keep design decisions in reusable layout/components, not scattered page-local styles.

## Anti-Patterns

- Generic admin template look with no TTCS identity.
- Overly decorative hero/marketing layout as the first screen.
- Decorative gradient blobs/orbs.
- Emoji as navigation or action icons.
- Placeholder-only form fields.
- Low-contrast gray-on-gray text.
- Cards nested inside cards.
- Phase 1 UI that fakes Phase 5 dashboard/workspace data.
- Dark blue/slate-only palette with no semantic accents.

## Pre-Implementation Checklist

- [ ] Read this design system before planning frontend work.
- [ ] Auth pages have visible labels, inline errors, loading state, and keyboard support.
- [ ] App shell is responsive and has no horizontal mobile scroll.
- [ ] All interactive controls have 44px minimum target or equivalent padding.
- [ ] Focus states are visible.
- [ ] Status colors have text/icon labels.
- [ ] Reduced motion is respected.
- [ ] No fake Phase 2/3/5 business data appears in Phase 1 UI.
