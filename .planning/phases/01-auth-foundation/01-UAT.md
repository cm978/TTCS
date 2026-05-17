---
status: testing
phase: 01-auth-foundation
source:
  - .planning/phases/01-auth-foundation/01-01-SUMMARY.md
  - .planning/phases/01-auth-foundation/01-02-SUMMARY.md
  - .planning/phases/01-auth-foundation/01-03-SUMMARY.md
  - .planning/phases/01-auth-foundation/01-04-SUMMARY.md
started: 2026-05-17T12:08:47Z
updated: 2026-05-17T12:08:47Z
---

## Current Test

number: 1
name: Open Login Page
expected: |
  Open http://127.0.0.1:5173/. You should see the TTCS login experience with a visible email field, visible password field, "登录 TTCS" primary action, and a link to create an account. The page should feel like the TTCS auth foundation, not a blank scaffold.
awaiting: user response

## Tests

### 1. Open Login Page
expected: Open http://127.0.0.1:5173/. You should see the TTCS login experience with a visible email field, visible password field, "登录 TTCS" primary action, and a link to create an account. The page should feel like the TTCS auth foundation, not a blank scaffold.
result: [pending]

### 2. Register New User
expected: Click the create-account link, fill display name, email, and password, then submit. You should land in the protected TTCS app shell and see current-user information without seeing any fake teams, projects, tasks, or dashboard metrics.
result: [pending]

### 3. Login Existing User
expected: Log out if needed, then log in with demo@example.com and DemoPass123!. You should enter the protected app shell and see "基础认证已就绪" with current-user information.
result: [pending]

### 4. Refresh Session Recovery
expected: While logged in on the protected app shell, refresh the browser. You should remain in the protected shell and the current-user information should still load through the saved JWT session.
result: [pending]

### 5. Logout Blocks Protected Route
expected: Click "退出登录". You should return to the login screen. Visiting /app again should redirect back to login instead of showing protected content.
result: [pending]

### 6. Auth API Technical Check
expected: The backend should respond at http://127.0.0.1:8000/api/v1/health with status ok, and the UI flow should use the backend auth API rather than mock-only behavior.
result: [pending]

### 7. Cold Start Smoke Test
expected: From a stopped state, the backend can run migrations/seed and boot, the frontend can boot, the homepage loads, and the auth API supports register, login, and /me. In this environment Docker-backed MySQL/Redis may be blocked if Docker is unavailable.
result: [pending]

## Summary

total: 7
passed: 0
issues: 0
pending: 7
skipped: 0
blocked: 0

## Gaps

[none yet]

