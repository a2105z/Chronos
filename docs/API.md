# API Reference

This document describes the REST API exposed by the Chronos backend. All endpoints are under `/api` and return JSON unless noted.

**Base URL (local):** `http://localhost:8000`

**Interactive docs:** `http://localhost:8000/docs` (Swagger UI)

---

## Tasks

### List tasks
```
GET /api/tasks
```
Returns all tasks, newest first.

**Response:** Array of task objects.

---

### Create task
```
POST /api/tasks
Content-Type: application/json
```

**Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Task name |
| estimated_duration_minutes | integer | Yes | Duration in minutes (min 1) |
| priority | integer | No | Default 0. Higher = more important. |
| deadline | ISO datetime string | No | When the task must be done. |
| splittable | boolean | No | Default false. If true, task can span multiple blocks. |

**Example:**
```json
{
  "name": "Study for exam",
  "estimated_duration_minutes": 120,
  "priority": 1,
  "splittable": true
}
```

**Response:** Created task with id, timestamps, etc.

---

### Get task
```
GET /api/tasks/{task_id}
```
Returns a single task by ID.

**Response:** Task object or 404.

---

### Update task
```
PUT /api/tasks/{task_id}
Content-Type: application/json
```
Partial updates supported. Only include fields you want to change.

**Example:**
```json
{
  "name": "Study for final exam",
  "estimated_duration_minutes": 90
}
```

**Response:** Updated task.

---

### Delete task
```
DELETE /api/tasks/{task_id}
```
**Response:** 204 No Content on success, 404 if not found.

---

## Availability

### List availability windows
```
GET /api/availability
```
Returns all availability windows, ordered by day and start time.

---

### Create availability window
```
POST /api/availability
Content-Type: application/json
```

**Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| day_of_week | integer | Yes | 0 = Monday, 6 = Sunday |
| start_minutes | integer | Yes | Minutes from midnight (0–1440). E.g., 540 = 9:00 AM. |
| end_minutes | integer | Yes | Minutes from midnight. Must be greater than start_minutes. |

**Example:**
```json
{
  "day_of_week": 0,
  "start_minutes": 540,
  "end_minutes": 1020
}
```
(Monday 9:00 AM – 5:00 PM)

---

### Get availability window
```
GET /api/availability/{window_id}
```

---

### Update availability window
```
PUT /api/availability/{window_id}
Content-Type: application/json
```
Partial updates supported. start_minutes must remain less than end_minutes.

---

### Delete availability window
```
DELETE /api/availability/{window_id}
```
**Response:** 204 No Content.

---

## Constraints

### List constraints
```
GET /api/constraints
```

---

### Create constraint
```
POST /api/constraints
Content-Type: application/json
```

**Body:** Depends on `constraint_type`.

#### Protected block (e.g., lunch)
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| constraint_type | string | Yes | "protected_block" |
| day_of_week | integer | Yes | 0–6 |
| start_minutes | integer | Yes | 0–1440 |
| end_minutes | integer | Yes | Must be > start_minutes |

**Example:**
```json
{
  "constraint_type": "protected_block",
  "day_of_week": 0,
  "start_minutes": 720,
  "end_minutes": 780
}
```
(Monday 12:00–13:00 lunch block)

#### Max continuous work
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| constraint_type | string | Yes | "max_continuous_work" |
| value | integer | Yes | Max minutes per block (min 1) |

**Example:**
```json
{
  "constraint_type": "max_continuous_work",
  "value": 60
}
```

---

### Get constraint
```
GET /api/constraints/{constraint_id}
```

---

### Update constraint
```
PUT /api/constraints/{constraint_id}
Content-Type: application/json
```
Partial updates supported.

---

### Delete constraint
```
DELETE /api/constraints/{constraint_id}
```
**Response:** 204 No Content.

---

## Schedule

### Generate schedule
```
POST /api/schedule
Content-Type: application/json
```

**Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| start_date | ISO datetime string | Yes | Start of date range (e.g., "2025-01-06T00:00:00") |
| end_date | ISO datetime string | Yes | End of date range |
| replace_existing | boolean | No | Default true. Reserved for future use. |

**Example:**
```json
{
  "start_date": "2025-01-06T00:00:00",
  "end_date": "2025-01-12T00:00:00"
}
```

**Response:** Array of scheduled blocks:
```json
[
  {
    "id": 1,
    "task_id": 1,
    "task_name": "Study",
    "start_time": "2025-01-06T09:00:00",
    "end_time": "2025-01-06T10:00:00",
    "duration_minutes": 60
  },
  ...
]
```

---

### Export schedule as .ics
```
POST /api/schedule/export
Content-Type: application/json
```

**Body:** Same as generate schedule (start_date, end_date).

**Response:** Binary .ics file.  
Content-Type: `text/calendar`  
Content-Disposition: `attachment; filename=chronos_schedule.ics`

You can import this into Google Calendar, Apple Calendar, Outlook, etc.

---

## Error Responses

- **404 Not Found** — Resource (task, availability, constraint) does not exist.
- **422 Unprocessable Entity** — Validation error (e.g., invalid fields, constraint validation).
- **500 Internal Server Error** — Server-side error.

Validation errors include a `detail` field describing what went wrong.
