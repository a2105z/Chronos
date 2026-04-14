# Backend

The backend is a FastAPI service in `backend/app/`. It handles validation, persistence, scheduling, and export.

## Stack

- FastAPI
- SQLModel + SQLite
- Pydantic

## Core folders

- `api/` - route handlers
- `models/` - database tables
- `schemas/` - request/response models
- `services/` - scheduling and export logic
- `db.py` - engine/session setup
- `main.py` - app bootstrapping and router registration

## Data model summary

- `Task` - work item metadata (duration, priority, time constraints)
- `AvailabilityWindow` - recurring free-time windows
- `Constraint` - protected blocks or max continuous work
- `ScheduledBlock` - generated calendar result stored in DB

## Main endpoints

- `/api/tasks` - CRUD for tasks
- `/api/availability` - CRUD for availability windows
- `/api/constraints` - CRUD for constraints
- `/api/schedule` - read/generate/move/delete schedule blocks
- `/api/schedule/export` - export persisted blocks as `.ics`

## Scheduling and validation

- Scheduler entry: `services/scheduler/engine.py`
- Slot creation: `services/scheduler/slots.py`
- Allocation: `services/scheduler/allocator.py`
- Hard-constraint checks for manual moves: `services/schedule_validation.py`

## Export

- `services/export/service.py` converts `ScheduledBlockRead` records into RFC 5545-compatible `.ics` bytes.

## Tests

Backend tests live in `backend/tests/` and are run with:

```bash
cd backend
pytest
```

For deeper test flow and acceptance coverage, see `docs/TESTING.md`.
