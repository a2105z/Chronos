# Chronos frontend

React + TypeScript + Vite UI for Chronos.

## Views

| View | Purpose |
|------|---------|
| **Plan** (default) | Natural-language composer → `POST /api/ai/plan` |
| **Calendar** | FullCalendar week grid, drag-move, unscheduled sidebar |
| **Tasks / Availability / Constraints** | Manual CRUD when you want precision |

## Design

- Fonts: **Syne** (brand) + **Manrope** (UI)
- Light mist paper + deep ink + teal signal accent
- Brand-first Plan and Auth surfaces; motion on focus / results / calendar load

## Scripts

```bash
npm install
npm run dev
npm test -- --run
npm run build
```

Vite proxies `/api` → `http://localhost:8000`.
