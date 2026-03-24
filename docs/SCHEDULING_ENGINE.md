# The Scheduling Engine: How It Works

This document explains the brain of Chronos — how we turn your tasks and availability into a conflict-free schedule. No math-heavy theory; just plain English and step-by-step logic.

---

## What Problem Are We Solving?

You have:
- A list of **tasks** (each with a duration, maybe a deadline, maybe splittable)
- **Availability windows** (when you're free, e.g., Monday 9am–5pm)
- **Constraints** (e.g., lunch 12–1pm is blocked, no work block longer than 60 minutes)

We need to produce a **schedule** — a list of time blocks, each assigned to a task — such that:
1. No two blocks overlap
2. Every block falls within your availability
3. No block overlaps a protected time (e.g., lunch)
4. No single block exceeds the max continuous work limit (if set)

---

## The Three Phases

The scheduling engine works in three phases:

1. **Gather data** — Load tasks, availability, and constraints from the database
2. **Build slots** — Turn availability into 15-minute chunks, excluding protected blocks
3. **Allocate tasks** — Greedily place tasks into slots, one at a time, never overlapping

Let's go through each phase.

---

## Phase 1: Gather Data (engine.py)

The `SchedulingEngine` is given a database session. When you call `generate(startDate, endDate)`:

1. **Fetch tasks** — All tasks from the DB, ordered by creation time
2. **Fetch availability** — All availability windows (e.g., Monday 9–5, Tuesday 9–5)
3. **Fetch constraints** — All constraints (protected blocks, max_continuous_work)

If there are no tasks or no availability, we return an empty schedule immediately. No point running the algorithm.

---

## Phase 2: Build Slots (slots.py)

**Goal:** Turn "Monday 9am–5pm" into a list of 15-minute chunks we can assign work to. And skip any chunk that overlaps a protected block (e.g., lunch 12–1pm).

### How buildAvailableSlots Works

1. **Extract protected blocks** — From constraints, keep only those of type `protected_block` (e.g., lunch 12–1pm).

2. **Loop over each day** in the date range (startDate to endDate).

3. **For each day**, find all availability windows that apply (e.g., if it's Monday, use the "Monday 9–5" window).

4. **For each window**, chop it into 15-minute slots:
   - Start at 9:00, then 9:15, 9:30, ... up to 5:00
   - Each slot is a pair: (start_time, end_time)

5. **Clip slots** to the requested date range. If you asked for Jan 6–12, we don't include slots outside that range.

6. **Skip blocked slots** — For each slot, check: does it overlap any protected block? If yes, don't include it. If no, add it to the list.

7. **Return** the final list of (start, end) slot pairs.

**Example:**  
Availability: Monday 9am–5pm. Protected: 12–1pm (lunch).  
Slots: 9:00–9:15, 9:15–9:30, ... 11:45–12:00, **skip 12:00–12:15 ... 12:45–1:00**, then 1:00–1:15, ... 4:45–5:00.

---

## Phase 3: Allocate Tasks (allocator.py) — The Greedy Algorithm

**Goal:** Place each task into one or more slots so that:
- Nothing overlaps
- Splittable tasks can span multiple blocks
- Non-splittable tasks get one contiguous block (or are split only if max_continuous_work forces it)
- We respect max_continuous_work (no block longer than X minutes)

### What "Greedy" Means

We process tasks **one at a time**, in a fixed order. For each task, we make the best choice *right now* without looking ahead. We never backtrack. That's why it's "greedy" — we grab the first good option and move on.

### Step 1: Order the Tasks

We want urgent and important tasks to get first pick of the best slots.

**Ordering rule:**
1. Tasks **with a deadline** come first, soonest deadline first. Among those with the same deadline, higher priority first.
2. Tasks **without a deadline** come next, ordered by priority (higher first).

### Step 2: Allocate One Task at a Time

For each task (in that order):

- **Track used ranges** — We keep a list of (start, end) time ranges that are already assigned. No new block can overlap these.

- **Two allocation strategies:**
  - **Splittable** — The task can be split across multiple blocks (e.g., 2 hours → 1hr + 1hr).
  - **Fixed (non-splittable)** — The task needs one contiguous block. Exception: if max_continuous_work is 60 and the task is 90 minutes, we *must* split it to satisfy the constraint.

### How allocateSplittable Works

For a splittable task (or a fixed task that must be split due to max_continuous_work):

1. Loop through slots in order (chronologically).
2. For each slot:
   - If we've already allocated the full task duration, stop.
   - If the slot overlaps any used range, skip it.
   - Compute how many minutes we can take: min(remaining needed, slot length, max_continuous_work).
   - If that's > 0, create a block, add it to the list, mark the range as used, subtract from remaining.
3. Continue until the task is fully allocated or we run out of slots.

**Example:** Task "Study" 90 min, splittable, max_continuous_work = 60.  
We might place: 9:00–10:00 (60 min), then 10:15–10:45 (30 min). Total 90 min, no block > 60.

### How allocateFixed Works

For a non-splittable task that fits in one block (duration ≤ max_continuous_work, or no limit):

1. We look for a **contiguous run** of slots — slots that are back-to-back with no gaps.
2. As we scan slots, we either start a new run or extend the current run.
3. If a slot overlaps used ranges, we reset the run (can't extend through blocked time).
4. When we've accumulated enough contiguous minutes to cover the task, we create one block and stop.

**Example:** Task "Meeting" 60 min, non-splittable.  
We need 4 consecutive 15-min slots. We find 9:00–9:15, 9:15–9:30, 9:30–9:45, 9:45–10:00. One block: 9:00–10:00.

### Step 3: Return the Blocks

The allocator returns a list of `AllocatedBlock` objects. The engine converts these to `ScheduledBlockRead` (the API format) and returns them to the caller.

---

## Constraint Enforcement Summary

| Constraint | Where it's enforced |
|------------|---------------------|
| **Protected blocks** (e.g., lunch) | In **slots.py** — blocked slots never make it into the slot list. The allocator never sees them. |
| **Max continuous work** | In **allocator.py** — when creating a block, we cap its duration at the limit. For fixed tasks that exceed the limit, we use the splittable path instead. |
| **No overlaps** | In **allocator.py** — we track `usedRanges` and skip any slot that overlaps. |
| **Within availability** | Guaranteed by **slots.py** — we only create slots from availability windows, so every block is within your free time. |

---

## File-by-File Summary

| File | Role |
|------|------|
| **engine.py** | Orchestrator. Fetches data, calls slots + allocator, converts output to API format. |
| **slots.py** | Builds 15-min slots from availability. Excludes protected blocks. |
| **allocator.py** | Greedy allocation. Orders tasks, places them into slots, enforces max_continuous_work and no overlap. |
| **constraints.py** | Helpers: get max continuous work value from constraints; validators for testing (no overlap, within availability, etc.). |

---

## A Walkthrough Example

**Input:**
- Tasks: "Study" 120 min (splittable), "Meeting" 60 min (fixed)
- Availability: Monday 9am–5pm
- Constraints: Lunch 12–1pm blocked, max 60 min work blocks

**Slots:** 9:00–9:15, 9:15–9:30, ... 11:45–12:00, *[12:00–1:00 skipped]*, 1:00–1:15, ... 4:45–5:00

**Order:** Meeting first (assume it has a deadline), then Study.

**Allocation:**
1. **Meeting** (60 min, fixed): Needs 4 contiguous 15-min slots. Place at 9:00–10:00. Mark 9:00–10:00 as used.
2. **Study** (120 min, splittable, max 60): First block 10:00–11:00 (60 min). Second block 11:15–12:00 (45 min) … wait, 11:15–12:00 is only 45 min and we need 60 more. So: 10:00–11:00 (60), 1:00–2:00 (60). Total 120. Mark those ranges used.

**Output:** Three blocks — Meeting 9–10, Study 10–11, Study 1–2.

---

## Why This Approach?

- **Simple** — Easy to reason about and debug.
- **Fast** — One pass over tasks, one pass over slots per task. No complex optimization.
- **Deterministic** — Same input always gives the same output.
- **Constraint-respecting** — Protected blocks and max continuous work are built in.

Trade-off: We don't optimize for "best" schedule (e.g., minimizing fragmentation). We produce a *valid* schedule quickly. For most personal use cases, that's enough.
