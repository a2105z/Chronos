# Testing

This is the practical test checklist for Chronos.

## Backend

```bash
cd backend
pytest
pytest --cov=app
```

Focus areas:

- CRUD behavior for tasks, availability, constraints
- scheduler invariants (no overlap, within availability)
- hard-constraint handling (protected blocks, max continuous work)
- edge cases (earliest start, missed deadlines, time-of-day preference)
- `.ics` export behavior

## Frontend

```bash
cd frontend
npm test -- --run
npm run test:coverage
```

Focus areas:

- app shell rendering
- calendar grouping utilities for scheduled and unscheduled tasks

## Manual smoke test

1. Create/edit/delete tasks.
2. Add availability and constraints.
3. Generate schedule.
4. Try one valid move and one invalid move.
5. Export `.ics` and confirm file downloads.

Use `tests/manual/demo_checklist.md` before demos.
