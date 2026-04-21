# Scheduling Engine

This is the core logic that turns tasks into calendar blocks.

## What goes in

- tasks
- availability windows
- constraints
- requested date range

## What comes out

- persisted `ScheduledBlock` rows for the range
- no overlaps
- no violations of hard constraints

## How it works

1. `engine.py` loads tasks, availability, and constraints.
2. `slots.py` builds 15-minute slots from availability.
3. Protected blocks are filtered out at slot build time.
4. `allocator.py` orders tasks and picks block placements.
5. Chosen blocks are saved through `schedule_persistence.py`.

## Allocation strategy (current)

The allocator is still greedy, but no longer first-fit.

- It now scores candidates and picks the best one.
- It uses a sorted interval timeline for overlap checks.
- It can switch style based on workload:
  - `balanced`
  - `deadline_focus`
  - `deep_work`

Scoring considers:

- deadline slack / lateness
- task priority
- time-of-day preference match
- continuity (reduce fragmentation)
- chunk usefulness for remaining work

## Hard rules always enforced

- no block overlap
- inside availability windows
- protected blocks excluded
- max continuous work respected
- task constraints respected (`earliest_start`, `deadline`, `preferred_time_of_day`)

## Key files

- `backend/app/services/scheduler/engine.py`
- `backend/app/services/scheduler/slots.py`
- `backend/app/services/scheduler/allocator.py`
- `backend/app/services/scheduler/intervals.py`
- `backend/app/services/scheduler/scoring.py`
