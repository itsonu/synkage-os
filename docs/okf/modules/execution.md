---
type: Module
title: Execution routing layer
description: Maps tasks to adapters and enforces autonomy policy, confirmation, and rollback.
timestamp: 2026-09-24T18:58:38Z
sources:
  - synkage/execution/__init__.py
  - synkage/execution/confirmation_loop.py
---

## Status
in-progress — confirmation loop built in [Phase 1](../../phases/phase-01-brain.md); router, planner, rollback, audit log planned for [Phase 4](../../phases/phase-04-routing.md).

## Responsibilities
- Map task → [adapter](adapters.md).
- Apply autonomy thresholds from the [autonomy policy](../data-models/autonomy-policy.md).
- Run the [confirmation loop](../flows/confirmation-loop.md).
- Support undo / rollback where possible.
- Write an audit record for every execution (intent, tool, autonomy level, confirmation state, result).

## Files
- `confirmation_loop.py` — built: `confirm(plan, tool_target, ask, show) -> ConfirmationResult`. See [confirmation loop](../flows/confirmation-loop.md).
- `action_planner.py`, `autonomy_router.py`, `rollback.py` — planned.
