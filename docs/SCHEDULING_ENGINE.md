# Scheduling Engine

The scheduler converts tasks + availability + constraints into persisted `ScheduledBlock` records.

## Inputs

- Tasks (`Task`)
- Availability windows (`AvailabilityWindow`)
- Constraints (`Constraint`)
- Requested date range (`start_date`, `end_date`)

## Output

- A list of non-overlapping scheduled blocks inside the requested range

## Pipeline

1. **Load data** in `engine.py`.
2. **Build 15-minute slots** in `slots.py` from availability windows.
3. **Remove protected time** while building slots.
4. **Order tasks** by deadline/priority in `allocator.py`.
5. **Allocate blocks greedily** without overlaps.
6. **Apply max continuous work limit** when present.
7. **Persist blocks** via `schedule_persistence.py`.

## Behavior rules

- Blocks never overlap.
- Blocks stay inside availability.
- Protected blocks are never used.
- If a non-splittable task exceeds max continuous work, it is split to satisfy the hard limit.
- Task time constraints (`earliest_start`, `deadline`, `preferred_time_of_day`) are respected.

## Why this design

- Fast and deterministic for local planning.
- Easy to reason about and test.
- Strong hard-constraint guarantees.

## Where to look in code

- `backend/app/services/scheduler/engine.py`
- `backend/app/services/scheduler/slots.py`
- `backend/app/services/scheduler/allocator.py`
- `backend/app/services/scheduler/constraints.py`
