---
type: Module
title: Execution routing layer
description: Maps tasks to adapters and enforces autonomy policy, confirmation, and rollback.
timestamp: 2026-09-24T18:48:53Z
sources:
  - synkage/execution/__init__.py
---

## Status
scaffolded — planned for [Phase 1](../../phases/phase-01-brain.md) (confirmation loop) and [Phase 4](../../phases/phase-04-routing.md).

## Responsibilities
- Map task → [adapter](adapters.md).
- Apply autonomy thresholds from the [autonomy policy](../data-models/autonomy-policy.md).
- Run the [confirmation loop](../flows/confirmation-loop.md).
- Support undo / rollback where possible.
- Write an audit record for every execution (intent, tool, autonomy level, confirmation state, result).

## Planned files
`action_planner.py`, `autonomy_router.py`, `confirmation_loop.py`, `rollback.py`.
