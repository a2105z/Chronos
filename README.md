# Chronos

Intelligent constraint-aware time blocking engine.

Built by Aarav Mittal, Josh Olmos, Anjay Krishna, and Ojas Bankhele.

## What Chronos Does

Chronos takes tasks, availability windows, and scheduling constraints, then builds a conflict-free calendar plan.

- Generates schedules with no overlap.
- Stays inside configured availability windows.
- Applies hard constraints like protected blocks and max continuous work.
- Handles task priority, deadlines, and preferred time of day.
- Supports `.ics` export for calendar apps.

## Quick Start (Run the App Locally)

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm

### 1) Start the backend (Terminal 1)

```bash
cd backend
python -m venv venv
```

Activate the virtual environment:

- Windows PowerShell:

```bash
.\venv\Scripts\activate
```

- macOS/Linux:

```bash
source venv/bin/activate
```

Install dependencies and run FastAPI:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend URLs:

- API base: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`

### 2) Start the frontend (Terminal 2)

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:

- App: `http://localhost:5173`

The frontend calls `/api`, and Vite proxies that to `http://localhost:8000`.

### 3) Stop the app

- In each terminal, press `Ctrl + C`.

## Testing

### Backend tests

```bash
cd backend
pytest
pytest --cov=app
```

### Frontend tests

```bash
cd frontend
npx vitest run
```

## Common Issues

- `Address already in use` on port `8000` or `5173`: stop old processes and restart.
- Frontend starts but API calls fail: confirm backend is running on `localhost:8000`.
- Missing Python packages: make sure the backend virtual environment is activated before `pip install`.
- Node module errors: run `npm install` again in `frontend`.

## API Overview

- `GET/POST /api/tasks`
- `GET/PUT/DELETE /api/tasks/{id}`
- `GET/POST /api/availability`
- `GET/POST /api/constraints`
- `POST /api/schedule`
- `POST /api/schedule/export`

## Documentation

Full project docs are in `docs/`.

Recommended starting points:

- [Architecture](docs/ARCHITECTURE.md)
- [Scheduling Engine](docs/SCHEDULING_ENGINE.md)
- [API Reference](docs/API.md)
- [Testing Guide](docs/TESTING.md)
- [Demo Prep](docs/DEMO_PREP.md)
- [Docs Index](docs/README.md)

## Development Schedule (9 Weeks)

- Week 1: Project setup, architecture, CI - complete
- Week 2: Task CRUD, database persistence - complete
- Week 3: Availability and constraints modeling - complete
- Week 4: Core scheduling engine baseline - complete
- Week 5: Constraint enforcement and unit tests - complete
- Week 6: Frontend integration - complete
- Week 7: Calendar view and manual editing - complete
- Week 8: `.ics` export and cross-platform testing - complete
- Week 9: Refinement, edge cases, testing, docs, demo prep - complete

## Team

- Frontend Lead (Ojas Bankhele): React UI, calendar, user flows
- Backend Lead (Anjay Krishna): API, database, testing, documentation
- Scheduling Engine Lead (Aarav Mittal): algorithm and constraint handling
- Export and Integration Lead (Josh Olmos): `.ics` export and system integration

## License

MIT
