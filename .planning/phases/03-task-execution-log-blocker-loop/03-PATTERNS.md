# Phase 03 — Pattern Map

## Purpose

Pattern map for Phase 3 planning. Generated inline because `gsd-pattern-mapper` is not installed in this Codex runtime.

## Backend Analogs

| New File / Role | Closest Existing Analog | Pattern to Reuse |
|-----------------|-------------------------|------------------|
| `backend/app/models/task.py` | `backend/app/models/project.py` | SQLAlchemy 2 `Mapped` models, string enum classes, FK indexes, `created_at` / `updated_at`, explicit uniqueness constraints. |
| `backend/app/schemas/task.py` | `backend/app/schemas/project.py` | Pydantic v2 schemas with `ConfigDict(from_attributes=True)`, Literal value aliases, request validators. |
| `backend/app/services/task_service.py` | `backend/app/services/project_service.py` | Service class per domain, explicit domain errors, permission helpers before mutation, `commit()` in service methods, refresh before returning. |
| `backend/app/services/work_log_service.py` | `backend/app/services/project_service.py` | Business rule validation in service layer, transactionally update related denormalized fields. |
| `backend/app/api/v1/tasks.py` | `backend/app/api/v1/projects.py` | APIRouter, `get_current_user`, `get_db`, local error mapper, response models. |
| `backend/tests/test_task_execution.py` | `backend/tests/test_team_project.py` | Service tests plus API tests in one file, helper functions for auth and user creation. |
| Alembic migration | `backend/alembic/versions/20260517_0002_create_team_project_board.py` | Manual migration with table creation, indexes, FK constraints, downgrade in reverse order. |

## Frontend Analogs

| New File / Role | Closest Existing Analog | Pattern to Reuse |
|-----------------|-------------------------|------------------|
| `frontend/src/types/task.ts` | `frontend/src/types/project.ts` | Type aliases for enum-like string unions and interface-per-response structure. |
| `frontend/src/api/tasks.ts` | `frontend/src/api/projects.ts` | Thin `apiClient` wrappers returning typed data. |
| `frontend/src/stores/task.ts` | `frontend/src/stores/project.ts` | Pinia state with `loading`, `error`, active detail, and async actions. |
| `TaskDrawer.vue` | `ProjectMemberDrawer.vue` | Ant Design Vue drawer with permission-limited sections, visible copy, and scoped styles. |
| `TaskCard.vue` / board integration | `BoardColumn.vue`, `ProjectBoardView.vue` | Semantic status accents, column layout, loading/error board states. |
| `TaskDetailView.vue` | `ProjectBoardView.vue` | Protected route inside `AppLayout`, route param loading, alert/skeleton states. |
| frontend tests | `frontend/src/views/team-project.spec.ts` | Shallow component tests with mocked API modules and Pinia setup. |

## Integration Constraints

- Phase 3 task statuses must reuse Phase 2 board column statuses: `TODO`, `IN_PROGRESS`, `IN_REVIEW`, `REJECTED`, `DONE`; `CLOSED` and `DELETED` are not default board columns.
- API errors should map domain errors consistently with `projects.py`: `403`, `404`, `409`, and `400`.
- Frontend task UI must read `design-system/MASTER.md` and `03-UI-SPEC.md`; use semantic tokens and `lucide-vue-next`, not emoji structural icons.
- Tests must import new models through `app.models` / `backend/tests/conftest.py` so SQLite `Base.metadata.create_all()` sees the tables.

