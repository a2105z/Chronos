# Chronos Documentation

Welcome! This folder contains documentation that explains Chronos from the ground up. Whether you're new to the project or diving into a specific part, start here.

---

## What is Chronos?

Chronos turns your **to-do list** into a **realistic schedule**. You tell it what you need to do, when you're free, and any rules (like "no work longer than an hour without a break" or "lunch is always blocked"). Chronos then figures out *when* to do each task so nothing overlaps and everything fits.

---

## Documentation Index

| Document | What it covers |
|----------|----------------|
| [Architecture](ARCHITECTURE.md) | How the frontend, backend, database, and scheduler fit together. Start here for the big picture. |
| [Backend](BACKEND.md) | The Python API: tasks, availability, constraints, and how data flows through the server. |
| [Frontend](FRONTEND.md) | The React app: components, API client, and how users interact with Chronos. |
| [Scheduling Engine](SCHEDULING_ENGINE.md) | **The brain of Chronos** — how the greedy algorithm works, step by step. Read this to understand how schedules are built. |
| [API Reference](API.md) | All endpoints, request/response formats, and how to call the API. |

---

## Quick Start

1. Read [Architecture](ARCHITECTURE.md) for the overview.
2. Skim [Backend](BACKEND.md) and [Frontend](FRONTEND.md) to see what each side does.
3. Dive into [Scheduling Engine](SCHEDULING_ENGINE.md) to understand how scheduling actually works.

---

## Glossary

| Term | Meaning |
|------|---------|
| **Task** | Something you need to do. Has a name, estimated duration, optional deadline, and can be splittable or not. |
| **Availability window** | A recurring block of time when you're free (e.g., "Monday 9am–5pm"). |
| **Constraint** | A rule the scheduler must obey. Examples: protected blocks (lunch), max continuous work (60 min cap). |
| **Slot** | A 15-minute chunk of time that the scheduler can assign work to. |
| **Block** | A scheduled chunk of time assigned to a task. The output of the scheduler. |
