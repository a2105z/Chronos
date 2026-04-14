# Chronos Docs

Everything project-related lives in this folder so it is easy to navigate in one place.

## Start here

1. Read `ARCHITECTURE.md` for the system overview.
2. Read `BACKEND.md` and `FRONTEND.md` for implementation details.
3. Read `SCHEDULING_ENGINE.md` to understand scheduling behavior.

## Doc index

- `ARCHITECTURE.md` - high-level system layout and data flow
- `BACKEND.md` - FastAPI app structure, routes, and services
- `FRONTEND.md` - React app structure, views, and API usage
- `SCHEDULING_ENGINE.md` - how tasks are ordered and allocated
- `API.md` - endpoint reference with request/response examples
- `CROSS_PLATFORM_TESTING.md` - `.ics` import checks for Apple/Outlook/Google
- `TESTING.md` - backend, frontend, and manual test checklist
- `DEMO_PREP.md` - short runbook for demos

## Core terms

- **Task**: unit of work with duration and optional constraints
- **Availability window**: recurring free time (`day_of_week`, start, end)
- **Constraint**: scheduling rule (protected block or max continuous work)
- **Slot**: 15-minute candidate interval
- **Block**: persisted scheduled interval assigned to a task
