# Demo Prep

Use this short runbook before presenting.

## Start services

Backend:

```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```bash
cd frontend
npm run dev
```

Open:

- `http://127.0.0.1:5173`
- `http://127.0.0.1:8000/docs`

## Suggested demo flow

1. Show task creation with realistic examples.
2. Show availability windows.
3. Add one protected block and one max continuous work rule.
4. Generate schedule.
5. Move one block (valid), then try one invalid move.
6. Export `.ics`.

## Quick checks

- API and frontend both start cleanly.
- Calendar is not empty for demo week.
- Export file downloads successfully.
- Backend and frontend test suites are passing.
