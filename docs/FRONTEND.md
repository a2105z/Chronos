# Frontend

The frontend is a React + TypeScript app in `frontend/src/`. It collects user input, calls the API, and renders schedule data.

## Main entry points

- `main.tsx` - mounts the app
- `App.tsx` - top-level layout and view switching

## Views

- `components/tasks/` - create, edit, delete, and list tasks
- `components/availability/` - manage weekly availability windows
- `components/constraints/` - manage protected blocks and max continuous work
- `components/calendar/` - weekly schedule view, regenerate, move/delete blocks, `.ics` export

## API layer

API wrappers are in `src/api/`:

- `tasksApi.ts`
- `availabilityApi.ts`
- `constraintsApi.ts`
- `scheduleApi.ts`
- `client.ts` (shared exports)

The app uses relative `/api` requests, proxied to backend in development.

## Shared types and utilities

- `src/types/` keeps frontend contracts aligned with backend schemas.
- `src/utils/` contains date helpers and schedule grouping helpers used by calendar views.

## Tests

Frontend tests live in `frontend/tests/` and run with:

```bash
cd frontend
npm test -- --run
```

For coverage and manual acceptance flow, see `docs/TESTING.md`.
