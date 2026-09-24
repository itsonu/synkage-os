---
type: Phase
title: Execution routing
description: An intent routes through the autonomy router to an adapter and returns a normalised result.
timestamp: 2026-09-24T18:48:00Z
tags: [phase]
---

## Status
todo

## Goal
An intent routes through the autonomy router to an adapter and returns a normalised result.

## Scope
**In:** adapters/tool_adapter_base.py, local_exec_adapter, openclaw_adapter stub, execution/autonomy_router.py, action_planner.py, audit log.
**Out:** Real browser/desktop control, real OpenClaw calls.

## Acceptance criteria
Tick in `phases.json` with evidence when met.
- [ ] **ac-1** tool_adapter_base defines execute() → ExecutionResult; local_exec and openclaw stub implement it — tests pass
- [ ] **ac-2** Router picks the adapter named by the tool's registry entry — test passes
- [ ] **ac-3** Router refuses to execute an unconfirmed high/critical or never_autonomous action — test passes
- [ ] **ac-4** Every execution appends an audit record with intent, tool, autonomy level, confirmation state, result — test reads it back
- [ ] **ac-5** 'dry run' produces a plan and result without calling the adapter — test passes

## Depends on
[phase-03-skills](phase-03-skills.md)

## OKF concepts touched
- [modules/execution.md](../okf/modules/execution.md)
- [modules/adapters.md](../okf/modules/adapters.md)
- [data-models/tool-registry.md](../okf/data-models/tool-registry.md)

## Notes
plan.md Phase 4 (Week 5). Audit fields from docs/autonomy_safety.md.
