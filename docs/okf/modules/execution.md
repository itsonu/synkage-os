---
type: Module
title: Execution routing layer
description: Plans, gates, routes and audits every prepared action.
timestamp: 2026-09-25T13:31:09Z
sources:
  - synkage/execution/__init__.py
  - synkage/execution/confirmation_loop.py
  - synkage/execution/action_planner.py
  - synkage/execution/autonomy_router.py
  - synkage/execution/audit.py
---

## Status
in-progress — confirmation loop (Phase 1); action planner, autonomy router and audit log ([Phase 4](../../phases/phase-04-routing.md)). `rollback.py` is not built.

## Files
| File | Role |
|---|---|
| `confirmation_loop.py` | `confirm(plan, tool_target, ask, show)`; only `yes` confirms. See [confirmation loop](../flows/confirmation-loop.md) |
| `action_planner.py` | `ActionPlanner.plan(request, intent, decision) -> ExecutionPlan` (tool, adapter from the registry, risk, categories, `requires_confirmation`, blocked/unavailable/nothing-to-do). **Re-derives safety** instead of trusting the decision |
| `autonomy_router.py` | `AutonomyRouter.draft(...)` stages safe actions before confirmation; `AutonomyRouter.route(request, intent, decision, confirmation, run_id, drafted)` is the only place an action may run. `load_request(path)` reads a draft artifact file |
| `audit.py` | Append-only [audit log](../data-models/audit-log.md). Since Phase 6 each record carries the decision's `situation` |

Full order of checks: [execution routing](../flows/execution-routing.md).

## Connections
Uses [adapters](adapters.md) and the brain's [autonomy guard](autonomy-guard.md) (keyword matching). Called by the [CLI](cli.md) `run` and `shell` commands.
