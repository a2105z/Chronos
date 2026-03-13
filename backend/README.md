# Chronos Backend

Python FastAPI server for the Chronos scheduling engine.

---

## Quick Start

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

API: **http://localhost:8000**  
Interactive docs: **http://localhost:8000/docs**

---

## What Lives Here

| Folder/File | Purpose |
|-------------|---------|
| `app/main.py` | App entry point, CORS, routers |
| `app/db.py` | SQLite setup, session management |
| `app/models/` | Database models (Task, AvailabilityWindow, Constraint) |
| `app/schemas/` | Request/response validation |
| `app/api/` | REST endpoints (tasks, availability, constraints, schedule) |
| `app/services/scheduler/` | Scheduling engine (slots, allocator, constraints) |
| `app/services/export/` | .ics calendar export |
| `tests/` | Pytest tests |

---

## Run Tests

```bash
pytest
pytest --cov=app   # with coverage
```

---

## Full Documentation

See **[docs/](../docs/)** for detailed documentation:

- [Backend](docs/BACKEND.md) — Full backend walkthrough
- [Scheduling Engine](docs/SCHEDULING_ENGINE.md) — How the greedy algorithm works
- [API Reference](docs/API.md) — All endpoints
