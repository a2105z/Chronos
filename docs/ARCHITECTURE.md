# Chronos Architecture

This document explains how Chronos is put together — the pieces, how they talk to each other, and how data flows from your input to a final schedule.

---

## The Big Picture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER (You)                                     │
│  • Add tasks (Study 2hrs, Exercise 1hr)                                 │
│  • Set availability (Mon–Fri 9am–5pm)                                   │
│  • Add constraints (lunch 12–1, max 60 min work blocks)                 │
│  • Request a schedule                                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                                 │
│  • Task list: create, view, delete tasks                                │
│  • Calendar view: placeholder for future schedule display               │
│  • Talks to backend via HTTP (Axios)                                    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │  HTTP (JSON)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         BACKEND (FastAPI)                                │
│  • API routes: tasks, availability, constraints, schedule               │
│  • Database: SQLite (tasks, availability windows, constraints)          │
│  • Scheduling Engine: the core logic that builds the schedule           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              ┌──────────┐   ┌──────────┐   ┌──────────────┐
              │  Tasks   │   │Availability│  │ Constraints  │
              │   DB     │   │   Windows  │  │     DB       │
              └──────────┘   └──────────┘   └──────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    SCHEDULING ENGINE (Python)                            │
│  1. Load tasks, availability, constraints from DB                       │
│  2. Build 15-min slots (skip protected blocks)                          │
│  3. Run greedy allocator: place tasks into slots, no overlaps           │
│  4. Return list of blocks (or export as .ics)                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Three Main Layers

### 1. Frontend (React + TypeScript)

**Location:** `frontend/src/`

The user interface. Right now it has:
- A **Task List** where you add, view, and delete tasks
- A **Calendar** tab (placeholder; will show the schedule later)
- An **API client** that sends requests to the backend

The frontend does *not* do any scheduling. It just displays data and lets users create/edit tasks, availability, and constraints. When you want a schedule, it asks the backend.

---

### 2. Backend (FastAPI + Python)

**Location:** `backend/app/`

The server. It:
- Exposes REST APIs for tasks, availability, constraints, and schedule generation
- Stores data in SQLite
- Runs the scheduling engine when you request a schedule

Main parts:
- **`api/`** — HTTP route handlers (what URLs do what)
- **`models/`** — Database tables (Task, AvailabilityWindow, Constraint)
- **`schemas/`** — Request/response shapes (validation, JSON format)
- **`services/`** — Business logic (scheduling engine, .ics export)
- **`db.py`** — Database connection and session setup

---

### 3. Scheduling Engine (Python)

**Location:** `backend/app/services/scheduler/`

The brain. It takes tasks + availability + constraints and produces a conflict-free schedule. See [SCHEDULING_ENGINE.md](SCHEDULING_ENGINE.md) for the full story.

---

## Data Flow: From Task to Schedule

1. **You create a task** (e.g., "Study for 2 hours, splittable").
   - Frontend sends `POST /api/tasks` with the task data.
   - Backend saves it in the `tasks` table.

2. **You set availability** (e.g., "Monday 9am–5pm").
   - Frontend sends `POST /api/availability`.
   - Backend saves it in `availability_windows`.

3. **You add constraints** (e.g., "Lunch 12–1pm is blocked", "Max 60 min work blocks").
   - Frontend sends `POST /api/constraints`.
   - Backend saves them in `constraints`.

4. **You request a schedule** (e.g., "Give me a schedule for Jan 6–12").
   - Frontend sends `POST /api/schedule` with start and end dates.
   - Backend loads tasks, availability, constraints from the DB.
   - The **Scheduling Engine** builds slots, runs the allocator, and returns blocks.
   - Frontend receives the list of blocks (to display or export).

---

## Where Things Live

| Concern | Location | Files |
|---------|----------|-------|
| App entry point | Backend | `main.py` |
| Task CRUD | Backend | `api/tasks.py`, `models/task.py` |
| Availability CRUD | Backend | `api/availability.py`, `models/availability.py` |
| Constraint CRUD | Backend | `api/constraints.py`, `models/constraint.py` |
| Schedule generation | Backend | `api/schedule.py` |
| Slot building | Backend | `services/scheduler/slots.py` |
| Task allocation (greedy) | Backend | `services/scheduler/allocator.py` |
| Constraint logic | Backend | `services/scheduler/constraints.py` |
| .ics export | Backend | `services/export/service.py` |
| React app | Frontend | `App.tsx`, `components/` |
| API calls | Frontend | `api/client.ts` |
| Type definitions | Frontend | `types/` |

---

## Next Steps

- **Backend details:** [BACKEND.md](BACKEND.md)
- **Frontend details:** [FRONTEND.md](FRONTEND.md)
- **How scheduling works:** [SCHEDULING_ENGINE.md](SCHEDULING_ENGINE.md)
