# Checkpoint 2 Report

## Main Theme: Backend Foundation and Task CRUD
Checkpoint 2 was where Chronos became a real backend system instead of just a plan. We implemented task persistence and full CRUD routes so the app could create, read, update, and delete task records consistently.

This checkpoint also included recovering from an early setback when the repo was deleted. That interruption slowed us down, but we rebuilt the structure and continued with cleaner organization and better discipline on file layout.

## Main Contributor
**Anjay Krishna (Backend Lead)** led most of this checkpoint, especially backend model/schema/API flow and validation behavior.

## Files Added / Expanded in This Phase
- `backend/app/models/task.py`
- `backend/app/schemas/task.py`
- `backend/app/api/tasks.py`
- `backend/app/services/schedule_persistence.py`
- `backend/tests/test_tasks.py`

## What Was Built
- Full task CRUD API endpoints.
- Task fields needed for scheduling logic:
  - name
  - estimated duration
  - priority
  - deadline
  - splittable flag
  - preferred time data
- Validation behavior to reject malformed or invalid payloads.
- Stable DB write/read flow backed by SQLModel + SQLite.

## Technical Notes
- Models and schemas were separated cleanly, which made API contracts more predictable.
- Task tests were added early to avoid backend regressions while scheduler complexity grew later.
- Persistence service functions made it easier to centralize DB behavior and keep route files cleaner.