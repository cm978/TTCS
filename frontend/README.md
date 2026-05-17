# TTCS Frontend

Vue 3 + Vite + TypeScript frontend for the Phase 1 authentication foundation.

## Commands

```bash
npm install
npm run dev
npm run typecheck
npm run test:unit -- --run
npm run build
```

The frontend calls `VITE_API_BASE_URL`, defaults to `http://localhost:8000/api/v1`, and stores only the JWT Bearer token in `localStorage` under `ttcs.access_token`.

The implemented UI is limited to login, registration, protected `AppLayout`, current-user display, and logout. It intentionally does not show fake teams, projects, tasks, dashboard metrics, or acceptance records.

