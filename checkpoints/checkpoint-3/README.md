# Checkpoint 3 Report

## Main Theme: Availability and Constraint Modeling
Checkpoint 3 is where Chronos started behaving like a realistic planner. Instead of only storing tasks, the backend now understood when a user is available and what time ranges must remain protected.

This checkpoint introduced the "rules of the world" for scheduling: recurring weekly windows, protected blocks, and max continuous work limits. That was a major jump in realism because the scheduler could now avoid obvious bad outputs (like scheduling through lunch or across unavailable hours).

## Main Contributor
**Anjay Krishna (Backend Lead)** was the main contributor for this phase, especially for modeling, route behavior, and validation rules.

## Files Added / Expanded in This Phase
- `backend/app/models/availability.py`
- `backend/app/schemas/availability.py`
- `backend/app/api/availability.py`
- `backend/app/models/constraint.py`
- `backend/app/schemas/constraint.py`
- `backend/app/api/constraints.py`
- `backend/app/services/scheduler/constraints.py`
- `backend/tests/test_availability.py`
- `backend/tests/test_constraints.py`

## What Was Built
- Recurring availability windows (weekly pattern).
- Protected block constraints for non-negotiable no-schedule zones.
- Max continuous work constraints to limit long uninterrupted sessions.
- Strong validation for:
  - time range ordering
  - constraint type correctness
  - required fields by constraint type

## Technical Notes
- Constraint validation logic was separated into scheduler service utilities so route handlers stayed focused.
- Tests covered both happy-path behavior and invalid payload handling.
- Availability and constraint APIs were designed to support future scheduler extension without changing client contracts.
