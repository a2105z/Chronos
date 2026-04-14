# Root Test Hub

This top-level `tests/` folder is the project-wide testing hub.

Automated tests remain close to each app for tooling compatibility:

- Backend tests: `backend/tests/`
- Frontend tests: `frontend/tests/`

Manual acceptance artifacts live here:

- `tests/manual/demo_checklist.md`

---

## Common Commands

Backend:

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
npm test -- --run
```

Both sides should pass before pushing release/demo commits.
