# Checkpoint 4 Report

## Main Theme: Core Scheduling Engine + Frontend Integration
Checkpoint 4 was the core implementation checkpoint. This is where Chronos began generating actual schedules instead of only storing inputs.

We built the slot-generation and allocation flow on the backend, then connected that flow to the frontend so users could run generation and view outputs in calendar form. This phase covered both algorithmic placement and practical usage flow.

## Main Contributor
**Aarav Mittal (Scheduling Engine Lead)** led engine implementation and the allocation strategy.  
**Ojas Bankhele (Frontend Lead)** handled the frontend side for showing and interacting with schedule results.

## Files Added / Expanded in This Phase
- `backend/app/services/scheduler/engine.py`
- `backend/app/services/scheduler/slots.py`
- `backend/app/services/scheduler/allocator.py`
- `backend/app/services/scheduler/intervals.py`
- `backend/app/services/scheduler/scoring.py`
- `backend/app/api/schedule.py`
- `frontend/src/components/calendar/CalendarView.tsx`
- `frontend/src/components/calendar/CalendarDayColumn.tsx`
- `frontend/src/utils/scheduleMaps.ts`
- `backend/tests/test_schedule.py`

## What Was Built
- 15-minute slot generation constrained by availability.
- Constraint-aware allocation (protected blocks and overlap avoidance).
- Priority/deadline-aware greedy scheduling behavior.
- Splittable task support when a single contiguous block is not feasible.
- Calendar display and interaction flow for generated schedule output.

## Technical Notes
- The scheduler flow was separated into focused modules (`slots`, `allocator`, `constraints`, `scoring`) for maintainability.
- Overlap checks and allocation scoring were kept explicit to make behavior tunable.
- API and UI were connected through stable schedule endpoints, so generation could be triggered from frontend actions directly.
