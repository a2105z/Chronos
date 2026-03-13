# Chronos

**Intelligent Constraint-Aware Time Blocking Engine**

_by Aarav Mittal, Josh Olmos, Anjay Krishna, and Ojas Bankhele_

---

## Overview

Chronos is a constraint-aware scheduling engine that converts a structured task list and user availability into a feasible, conflict-free, time-blocked calendar. It bridges the gap between manual planning (to-do lists) and fixed schedules by automatically placing work into open time while respecting user rules and preferences.

### Core Objectives

- **Generate valid schedules** — No overlaps, always within availability windows
- **Respect constraints** — Hard constraints strictly, soft preferences when possible
- **Support realistic planning** — Task splitting, breaks, priority/deadline ordering
- **Provide interactive UI** — View, move, delete, and regenerate blocks
- **Export to calendar apps** — .ics files for Google Calendar, Apple Calendar, Outlook

---

## Documentation

Full documentation lives in **[docs/](docs/)**. Start with:

- **[Architecture](docs/ARCHITECTURE.md)** — How everything fits together
- **[Scheduling Engine](docs/SCHEDULING_ENGINE.md)** — How the greedy algorithm works
- **[API Reference](docs/API.md)** — All endpoints

See [docs/README.md](docs/README.md) for the full index.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | TypeScript, React, FullCalendar, Axios |
| Backend | Python 3.11+, FastAPI, Pydantic, SQLModel |
| Database | SQLite (via SQLModel) |
| Export | icalendar (RFC 5545 .ics) |
| Testing | Jest, React Testing Library, Pytest |

---

## Project Structure

```
Chronos/
├── README.md
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── models/               # Database models
│   │   ├── schemas/              # Pydantic schemas
│   │   ├── api/                 # API routes
│   │   ├── services/            # Business logic
│   │   │   ├── scheduler/        # Scheduling engine
│   │   │   └── export/          # .ics export service
│   │   └── db.py                # Database setup
│   ├── tests/
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── api/
│   │   ├── types/
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
└── .github/
    └── workflows/
        └── ci.yml
```

---

## Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm
- **Git**

### Backend Setup

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: **http://localhost:8000/docs**

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

App: **http://localhost:5173**

### Run Tests

**Backend:**
```bash
cd backend
pytest
pytest --cov=app  # with coverage
```

**Frontend:**
```bash
cd frontend
npm test
```

---

## API Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tasks` | GET, POST | List and create tasks |
| `/api/tasks/{id}` | GET, PUT, DELETE | Get, update, delete task |
| `/api/availability` | GET, POST | Manage availability windows |
| `/api/constraints` | GET, POST | Manage constraints |
| `/api/schedule` | POST | Generate schedule |
| `/api/schedule/export` | POST | Export .ics file |

---

## Development Schedule (10 Weeks)

| Week | Focus | Status |
|------|-------|--------|
| 1 | Project setup, architecture, CI | ✅ |
| 2 | Task CRUD, database persistence | ✅ |
| 3 | Availability & constraints modeling | ✅ |
| 4 | Core scheduling engine (baseline) | ✅ |
| 5 | Constraint enforcement, unit tests | ✅ |
| 6 | Frontend integration | |
| 7 | Calendar view & manual editing | |
| 8 | .ics export, cross-platform testing | |
| 9 | Refinement, edge cases | |
| 10 | Testing, documentation, demo prep | |

---

## Team

| Role | Responsibility |
|------|----------------|
| Frontend Lead (Josh) | React UI, calendar, user flows |
| Backend Lead (Anjay) | API, database, validation |
| Scheduling Engine Lead (Aarav) | Algorithm, constraint handling |
| Export & Integration Lead (Ojas Bankhele) | .ics export, system integration |

---

## License

MIT
