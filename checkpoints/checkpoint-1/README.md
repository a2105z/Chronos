# Checkpoint 1 Report

## Main Theme: Planning, Scope, and Project Setup
Checkpoint 1 was the "make sure we are solving the right problem" phase. Before writing deep scheduling logic, we defined what Chronos actually needed to do in plain terms: take tasks, availability windows, and hard constraints, then produce a realistic calendar plan that someone could follow in real life.

This was also the point where we set guardrails for the semester. We decided early that Chronos should prioritize correctness over flashy behavior. That means no-overlap blocks, respecting protected time, and consistent API behavior came first. We intentionally treated that as non-negotiable because every later feature depends on it.

## Main Contributor
**Aarav Mittal (Scheduling Engine Lead)** led the early architecture and scheduler direction, while the full team aligned on structure and ownership.

## Files Added / Initialized in This Phase
- `README.md`
- `backend/app/main.py`
- `backend/app/db.py`
- `backend/app/api/__init__.py`
- `docs/ARCHITECTURE.md`
- `docs/README.md`

## What Was Built
- Initial repository structure for frontend, backend, and docs.
- Base FastAPI app setup and DB wiring entry points.
- Shared architecture notes so API and engine work would stay aligned.
- Team role breakdown to avoid overlap and unclear ownership.

## Technical Notes
- The backend was organized around models, schemas, API routes, and services from day one.
- Documentation was treated as part of development, not an afterthought.
- We set the API-first approach early so frontend integration later would be predictable.
