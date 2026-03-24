# Scheduling Engine

This folder contains the core scheduling logic for Chronos. It turns tasks + availability + constraints into a conflict-free schedule.

---

## Files

| File | Purpose |
|------|---------|
| **engine.py** | Orchestrator. Loads data, calls slots + allocator, converts output. |
| **slots.py** | Builds 15-min slots from availability. Excludes protected blocks. |
| **allocator.py** | Greedy task allocation. Places tasks into slots, no overlaps. |
| **constraints.py** | Helper: get max continuous work. Validators for tests. |

---

## Data Flow

```
engine.generate(startDate, endDate)
    │
    ├─► fetchTasks(), fetchConstraints()
    ├─► getAvailabilityWindows(session)
    │
    ├─► buildAvailableSlots(start, end, windows, constraints)   [slots.py]
    │       → List of (start, end) 15-min slot tuples
    │
    ├─► allocateTasks(tasks, slots, constraints)                [allocator.py]
    │       → List of AllocatedBlock
    │
    └─► toScheduledBlockReads(blocks)
            → List of ScheduledBlockRead (API format)
```

---

## Deep Dive

See **[docs/SCHEDULING_ENGINE.md](../../../../docs/SCHEDULING_ENGINE.md)** for a full, human-friendly explanation of how the greedy algorithm works.
