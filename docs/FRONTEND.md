# Frontend Documentation

The frontend is the React app users interact with. It talks to the backend API and displays data. This document explains how it's organized and what each part does.

---

## Overview

The frontend is built with:
- **React** — UI framework
- **TypeScript** — Type-safe JavaScript
- **Vite** — Build tool and dev server
- **Axios** — HTTP client for API calls

Everything lives under `frontend/src/`.

---

## Entry Points

### `main.tsx`
The React app entry point. Renders the root `App` component into the DOM.

### `App.tsx`
The main app component. It:
- Shows a header with the Chronos title and tagline
- Provides four sections: **Tasks**, **Availability**, **Constraints**, and **Calendar**
- Tracks the **Monday-based calendar week** shown in `CalendarView` (reset to “this week” when you open Calendar from another tab)
- Bumps a `calendarRefreshTrigger` when tasks change so the calendar can reload persisted blocks

---

## Components (`components/`)

### `TaskList.tsx`
The task management screen. It lets you:
- **View** all tasks (loaded from the API on mount)
- **Create** new tasks via a form (name, duration, priority, preferred time, splittable, finish window)
- **Edit** tasks via **Edit** → `TaskEditDialog` → `PUT /api/tasks/{id}`
- **Delete** tasks with a delete button

**Key functions:**
- `loadTasks()` — `GET /api/tasks`
- `handleCreate()` — `POST /api/tasks`
- `handleDelete(id)` — `DELETE /api/tasks/{id}`

### `TaskEditDialog.tsx`
Modal editor for an existing task (partial update).

### `AvailabilityView.tsx`
CRUD for recurring weekly availability windows (`day_of_week` 0 = Monday, `start_minutes` / `end_minutes`).

### `ConstraintsView.tsx`
Add/remove **protected blocks** and **max continuous work** rules.

### `CalendarView.tsx`
Weekly grid (Monday–Sunday) aligned with backend weekdays. It:
- Loads persisted blocks with `GET /api/schedule?start_date=&end_date=`
- **Regenerate** — `POST /api/schedule` for the visible week (replaces overlapping stored blocks)
- **Move** — `PATCH /api/schedule/blocks/{id}` with a new `start_time` (duration preserved; server validates constraints)
- **Delete** — `DELETE /api/schedule/blocks/{id}`
- **Export** — `POST /api/schedule/export` and downloads `chronos_schedule.ics`
- **Prev / Next week** — changes the range without leaving the page

### `CalendarDayColumn.tsx`
One day column: scheduled blocks (with actions) and unscheduled tasks for that day.

---

## API Client (`api/client.ts`)

A centralized place for all API calls. Uses Axios with a base URL of `/api` (so it works with the backend proxy in development).

**Tasks:**
- `getTasks()` — GET /tasks
- `createTask(data)` — POST /tasks
- `updateTask(id, data)` — PUT /tasks/{id}
- `deleteTask(id)` — DELETE /tasks/{id}

**Availability:**
- `getAvailability()` — GET /availability
- `createAvailability(data)` — POST /availability
- `updateAvailability(id, data)` — PUT /availability/{id}
- `deleteAvailability(id)` — DELETE /availability/{id}

**Constraints:**
- `getConstraints()` — GET /constraints
- `createConstraint(data)` — POST /constraints
- `updateConstraint(id, data)` — PUT /constraints/{id}
- `deleteConstraint(id)` — DELETE /constraints/{id}

**Schedule:**
- `getSchedule(startDate, endDate)` — GET /schedule (persisted blocks in range)
- `generateSchedule(startDate, endDate)` — POST /schedule (regenerate + persist)
- `moveScheduleBlock(id, startTimeIso)` — PATCH /schedule/blocks/{id}
- `deleteScheduleBlock(id)` — DELETE /schedule/blocks/{id}
- `exportSchedule(startDate, endDate)` — POST /schedule/export (returns .ics blob)

The frontend is configured (in Vite) to proxy `/api` requests to the backend at `localhost:8000`, so the client uses relative URLs.

---

## Types (`types/`)

TypeScript type definitions that match the backend schemas.

### `task.ts`
- **Task** — Full task object (id, name, estimated_duration_minutes, priority, optional earliest_start/deadline, splittable, etc.)
- **TaskCreate** — Create payload
- **TaskUpdate** — Partial update payload for `PUT /api/tasks/{id}`

### `availability.ts`
- **AvailabilityWindow** — day_of_week, start_minutes, end_minutes, id
- **AvailabilityCreate** — Same fields for creation

### `constraint.ts`
- **Constraint** — constraint_type, day_of_week, start_minutes, end_minutes, value, id, etc.
- **ConstraintCreate** — For creation

### `schedule.ts`
- **ScheduledBlock** — task_id, task_name, start_time, end_time, duration_minutes
- **ScheduleGenerateRequest** — start_date, end_date

These types ensure the frontend and backend agree on data shapes and catch mistakes at compile time.

---

## Styling

- **App.css** — Global app styles, header, nav tabs
- **TaskList.css** — Task list layout, form styling, buttons
- **CalendarView.css** — Weekly grid, block cards, move dialog
- **AvailabilityView.css**, **ConstraintsView.css** — Panel forms
- **TaskEditDialog.css** — Modal overlay
- **index.css** — Base styles (resets, fonts)

---

## File Summary

| File | Purpose |
|------|---------|
| `main.tsx` | React entry point |
| `App.tsx` | Root layout, four-way navigation, calendar week state |
| `components/tasks/TaskList.tsx` | Task list, create, edit, delete |
| `components/tasks/TaskEditDialog.tsx` | Edit task modal |
| `components/availability/AvailabilityView.tsx` | Availability CRUD |
| `components/constraints/ConstraintsView.tsx` | Constraints CRUD |
| `components/calendar/CalendarView.tsx` | Weekly schedule, regenerate, move/delete, export |
| `components/calendar/CalendarDayColumn.tsx` | Single-day column |
| `api/client.ts` | Re-exports API modules |
| `api/scheduleApi.ts` | Schedule + block endpoints |
| `types/app.ts` | `AppView` union |
| `types/task.ts` | Task / TaskCreate / TaskUpdate |
| `types/availability.ts` | Availability types |
| `types/constraint.ts` | Constraint types |
| `types/schedule.ts` | ScheduledBlock |

---

## Possible follow-ups

- **Drag-and-drop** block moves (currently explicit Move dialog + server validation).
- **FullCalendar** integration if you want a month/agenda layout in addition to the weekly grid.
- **Inline edit** for availability and constraints (currently add/remove; backend supports `PUT`).
