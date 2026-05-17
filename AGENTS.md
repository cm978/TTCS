<!-- GSD:project-start source:PROJECT.md -->
## Project

**TTCS**
<!-- GSD:project-end -->

<!-- GSD:stack-start source:STACK.md -->
## Technology Stack

Technology stack not yet documented. Will populate after codebase mapping or first phase.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

### UI/UX

Frontend work must follow `design-system/MASTER.md`, which adapts the `ui-ux-pro-max` skill for TTCS.

Key rules:
- Use a polished operational SaaS cockpit style, not a generic admin template.
- Prioritize accessibility: visible labels, focus states, 4.5:1 text contrast, keyboard navigation, and aria labels for icon-only buttons.
- Use semantic color/theme tokens instead of raw hex values scattered in components.
- Use vector icons from one consistent family; do not use emoji as structural UI icons.
- Keep touch/click targets at least 44px where practical.
- Provide loading, disabled, error, success, hover, focus, and pressed states for controls.
- Respect responsive layout rules and avoid horizontal mobile scroll.
- Do not fake Phase 2/3/5 data in Phase 1 UI.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
