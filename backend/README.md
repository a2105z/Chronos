# Chronos Backend

FastAPI service: JWT auth, AI planner, constraint scheduling engine.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
pytest -q
```

See root [README.md](../README.md) and [TECHNICAL.md](../TECHNICAL.md).
