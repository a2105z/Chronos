# Architecture

Chronos has three parts:

1. **Frontend (`frontend/`)** - React UI for tasks, availability, constraints, and calendar actions.
2. **Backend (`backend/app/`)** - FastAPI API + SQLite persistence.
3. **Scheduler (`backend/app/services/scheduler/`)** - builds valid blocks from tasks + rules.

## Request flow

1. User updates data in the UI.
2. Frontend calls backend endpoints under `/api/...`.
3. Backend stores data (`tasks`, `availability_windows`, `constraints`, `scheduled_blocks`).
4. On schedule generation, backend runs the scheduler and persists blocks.
5. Frontend reads persisted blocks for display, move/delete, and `.ics` export.

## Key boundaries

- Frontend does presentation and user actions only.
- Backend owns validation, persistence, and scheduling rules.
- Scheduler is pure business logic driven by DB data.

## Main files

- `backend/app/main.py` - app setup and router registration
- `backend/app/api/` - route handlers
- `backend/app/models/` - SQLModel tables
- `backend/app/schemas/` - request/response contracts
- `backend/app/services/scheduler/` - slot building, scored allocation, interval tracking
- `backend/app/services/export/service.py` - `.ics` generation
- `frontend/src/components/` - UI views
- `frontend/src/api/` - API client wrappers

## Related docs

- `BACKEND.md`
- `FRONTEND.md`
- `SCHEDULING_ENGINE.md`
