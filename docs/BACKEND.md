# Backend Documentation

The backend is the Python server that stores your data and runs the scheduling engine. This document walks through each part and what it does.

---

## Overview

The backend is built with:
- **FastAPI** — web framework for the API
- **SQLModel** — database models (works with SQLite)
- **Pydantic** — validation for request/response data

Everything lives under `backend/app/`.

---

## Entry Point: main.py

This is where the app starts. It:
1. Creates the FastAPI application
2. Sets up CORS (so the frontend at localhost:5173 can call the API)
3. Registers all the API routers (tasks, availability, constraints, schedule)
4. Runs database setup when the app starts (creates tables if needed)
5. Exposes a health check at GET /

---

## Database: db.py

The database is SQLite, stored in chronos.db in the backend folder.

**Key functions:**
- **createDbAndTables()** — Creates all tables if they don't exist. Called when the app starts.
- **getSession()** — Provides a database session for each API request. Ensures we use one connection per request and close it when done.

The models (Task, AvailabilityWindow, Constraint) are defined in models/ and SQLModel turns them into tables automatically.

---

## Models (models/)

These define what we store in the database.

### models/task.py — Task

A schedulable item. Fields:
- **name** — What the task is (e.g., "Study for exam")
- **estimated_duration_minutes** — How long it takes (must be at least 1)
- **priority** — Higher = more important (default 0)
- **deadline** — Optional. When it must be done. Used for ordering.
- **splittable** — If true, the task can be split across multiple time blocks. If false, it needs one contiguous block.
- **created_at**, **updated_at** — Timestamps

### models/availability.py — AvailabilityWindow

A recurring weekly window when you're free.
- **day_of_week** — 0 = Monday, 6 = Sunday
- **start_minutes** — Minutes from midnight (e.g., 540 = 9:00 AM)
- **end_minutes** — Minutes from midnight (e.g., 1020 = 5:00 PM)

Example: day_of_week 0, start 540, end 1020 = Monday 9am–5pm.

### models/constraint.py — Constraint

A rule the scheduler must follow. Two types:

1. **protected_block** — Time that must never be scheduled (e.g., lunch).
   - Requires: day_of_week, start_minutes, end_minutes

2. **max_continuous_work** — No single work block longer than X minutes.
   - Requires: value (the max minutes, e.g., 60)

---

## Schemas (schemas/)

Schemas define the shape of data for API requests and responses. They validate incoming JSON and format outgoing data.

- **Create schemas** — What the client sends when creating
- **Update schemas** — What the client sends when updating (partial updates allowed)
- **Read schemas** — What we send back (includes IDs, timestamps, etc.)

They also run validation. For example:
- Availability: start_minutes must be less than end_minutes
- Constraints: required fields depend on constraint_type (protected_block vs max_continuous_work)

---

## API Routes (api/)

Each file defines a set of endpoints.

### api/tasks.py
- GET /api/tasks — List all tasks (newest first)
- POST /api/tasks — Create a task
- GET /api/tasks/{id} — Get one task
- PUT /api/tasks/{id} — Update a task (partial updates OK)
- DELETE /api/tasks/{id} — Delete a task

### api/availability.py
- GET /api/availability — List all availability windows
- POST /api/availability — Create a window
- GET /api/availability/{id} — Get one window
- PUT /api/availability/{id} — Update a window
- DELETE /api/availability/{id} — Delete a window

### api/constraints.py
- GET /api/constraints — List all constraints
- POST /api/constraints — Create a constraint
- GET /api/constraints/{id} — Get one constraint
- PUT /api/constraints/{id} — Update a constraint
- DELETE /api/constraints/{id} — Delete a constraint

### api/schedule.py
- POST /api/schedule — Generate a schedule for a date range. Sends back a list of blocks.
- POST /api/schedule/export — Same as above, but returns an .ics file for calendar apps.

---

## Services (services/)

Business logic that does not belong in the API routes.

### services/availability.py
- **getAvailabilityWindows(session)** — Fetches all availability windows from the DB. Used by the scheduling engine.

### services/scheduler/
See SCHEDULING_ENGINE.md for the full explanation. In short:
- **engine.py** — Orchestrates everything: loads data, builds slots, runs allocator, converts to API format
- **slots.py** — Builds 15-minute slots from availability, excluding protected blocks
- **allocator.py** — Greedy algorithm that places tasks into slots
- **constraints.py** — Helper functions: get max continuous work limit, validate schedules

### services/export/service.py
- **ExportService.toIcs(blocks)** — Converts a list of scheduled blocks into .ics format for calendar apps.

---

## Utilities (utils.py)

- **applyPartialUpdate(model, data)** — Updates only the fields present in data. Used for partial updates (e.g., change only the task name without touching duration).

---

## Tests (tests/)

- **test_tasks.py** — Task CRUD
- **test_availability.py** — Availability CRUD
- **test_constraints.py** — Constraint CRUD
- **test_schedule.py** — Schedule generation and invariants (no overlap, within availability, etc.)
- **test_constraint_enforcement.py** — Unit tests for the constraint logic

Run with: pytest (from the backend/ folder)

---

## File Summary

| File | Purpose |
|------|---------|
| main.py | App entry, CORS, router registration |
| db.py | Database setup and session management |
| models/task.py | Task database model |
| models/availability.py | Availability window model |
| models/constraint.py | Constraint model |
| schemas/*.py | Request/response validation |
| api/tasks.py | Task endpoints |
| api/availability.py | Availability endpoints |
| api/constraints.py | Constraint endpoints |
| api/schedule.py | Schedule generation and export |
| services/availability.py | Fetch availability for scheduler |
| services/scheduler/* | Scheduling engine (see SCHEDULING_ENGINE.md) |
| services/export/service.py | .ics export |
| utils.py | Partial update helper |
