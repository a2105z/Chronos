# API Reference

Base URL (local): `http://localhost:8000`  
Swagger docs: `http://localhost:8000/docs`

All endpoints are under `/api`.

## Tasks

- `GET /api/tasks`
- `POST /api/tasks`
- `GET /api/tasks/{task_id}`
- `PUT /api/tasks/{task_id}`
- `DELETE /api/tasks/{task_id}`

Create/update fields:

- `name` (string, required on create)
- `estimated_duration_minutes` (int >= 1)
- `priority` (int >= 0)
- `earliest_start` (ISO datetime, optional)
- `deadline` (ISO datetime, optional)
- `preferred_time_of_day` (`anytime|morning|afternoon|evening`)
- `splittable` (boolean)

## Availability

- `GET /api/availability`
- `POST /api/availability`
- `GET /api/availability/{window_id}`
- `PUT /api/availability/{window_id}`
- `DELETE /api/availability/{window_id}`

Fields:

- `day_of_week` (`0..6`, Monday = 0)
- `start_minutes` (`0..1439`)
- `end_minutes` (`1..1440`, must be greater than `start_minutes`)

## Constraints

- `GET /api/constraints`
- `POST /api/constraints`
- `GET /api/constraints/{constraint_id}`
- `PUT /api/constraints/{constraint_id}`
- `DELETE /api/constraints/{constraint_id}`

Constraint types:

- `protected_block` with `day_of_week`, `start_minutes`, `end_minutes`
- `max_continuous_work` with `value` (minutes)

## Schedule

- `GET /api/schedule?start_date=...&end_date=...`  
  Returns persisted blocks in range.

- `POST /api/schedule`  
  Generates schedule for range and replaces overlapping persisted blocks.

- `PATCH /api/schedule/blocks/{block_id}`  
  Moves one block by setting `start_time`; duration is preserved.

- `DELETE /api/schedule/blocks/{block_id}`

- `POST /api/schedule/export`  
  Exports persisted blocks in range as `.ics` (`text/calendar`).

Request body for generate/export:

```json
{
  "start_date": "2030-01-07T00:00:00",
  "end_date": "2030-01-14T00:00:00"
}
```

## Common errors

- `404` - resource not found
- `422` - validation or rule violation
- `500` - unexpected server error
