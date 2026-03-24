# Chronos Frontend

React + TypeScript app for the Chronos scheduling engine.

---

## Quick Start

```bash
cd frontend
npm install
npm run dev
```

App: **http://localhost:5173**

Make sure the backend is running at **http://localhost:8000** (the frontend proxies `/api` to it).

---

## What Lives Here

| Folder/File | Purpose |
|-------------|---------|
| `src/App.tsx` | Root component, Tasks/Calendar tabs |
| `src/components/TaskList.tsx` | Task list, create, delete |
| `src/components/CalendarView.tsx` | Placeholder for schedule (not yet wired) |
| `src/api/client.ts` | API calls (tasks, availability, constraints, schedule) |
| `src/types/` | TypeScript types matching backend schemas |

---

## Scripts

| Command | Purpose |
|---------|---------|
| `npm run dev` | Start dev server |
| `npm run build` | Production build |
| `npm test` | Run Jest tests |

---

## Full Documentation

See **[docs/](../docs/)** for detailed documentation:

- [Frontend](docs/FRONTEND.md) — Component overview, API client, types
- [Architecture](docs/ARCHITECTURE.md) — How frontend and backend fit together
