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
- Provides two tabs: **Tasks** and **Calendar**
- Switches between `TaskList` and `CalendarView` based on the active tab
- Manages which tab is active with `useState`

---

## Components (`components/`)

### `TaskList.tsx`
The task management screen. It lets you:
- **View** all tasks (loaded from the API on mount)
- **Create** new tasks via a form (name, duration, priority, splittable)
- **Delete** tasks with a delete button

**State:**
- `tasks` — list of tasks from the API
- `loading` — whether we're fetching
- `showForm` — whether the create form is visible
- `formData` — current values in the form

**Key functions:**
- `loadTasks()` — Fetches tasks from `GET /api/tasks`
- `handleCreate()` — Submits new task via `POST /api/tasks`
- `handleDelete(id)` — Deletes via `DELETE /api/tasks/{id}`

### `CalendarView.tsx`
A placeholder for the future calendar. Currently shows a simple message: "Calendar view will display generated schedule blocks." It does not yet call the schedule API or display blocks.

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
- `generateSchedule(startDate, endDate)` — POST /schedule (returns blocks)
- `exportSchedule(startDate, endDate)` — POST /schedule/export (returns .ics blob)

The frontend is configured (in Vite) to proxy `/api` requests to the backend at `localhost:8000`, so the client uses relative URLs.

---

## Types (`types/`)

TypeScript type definitions that match the backend schemas.

### `task.ts`
- **Task** — Full task object (id, name, estimated_duration_minutes, priority, deadline, splittable, etc.)
- **TaskCreate** — What you send when creating (name, duration, priority, splittable; no id)

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
- **CalendarView.css** — Calendar placeholder styling
- **index.css** — Base styles (resets, fonts)

---

## File Summary

| File | Purpose |
|------|---------|
| `main.tsx` | React entry point |
| `App.tsx` | Root component, tab switching |
| `components/TaskList.tsx` | Task list, create, delete |
| `components/CalendarView.tsx` | Placeholder for schedule display |
| `api/client.ts` | All API calls |
| `types/task.ts` | Task types |
| `types/availability.ts` | Availability types |
| `types/constraint.ts` | Constraint types |
| `types/schedule.ts` | Schedule types |

---

## What's Not Yet Built

- **CalendarView** — Does not yet call `generateSchedule()` or display blocks. It's a placeholder.
- **Availability UI** — No screen to add/edit availability windows yet. Only tasks are managed in the UI.
- **Constraints UI** — No screen to add/edit constraints yet.
- **Schedule request UI** — No date picker or "Generate Schedule" button that calls the API.
- **.ics download** — No button to export the schedule as a file.

These will be covered in later weeks (Frontend integration, Calendar view, etc.).
