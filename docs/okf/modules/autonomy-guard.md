---
type: Module
title: Autonomy guard
description: Decides whether an intent may run and whether it needs confirmation.
timestamp: 2026-09-25T13:30:46Z
sources:
  - synkage/brain/autonomy_guard.py
---

## Status
built (Phase 1); situation input since [Phase 6](../../phases/phase-06-situation.md).

## Interface
`AutonomyGuard(config).decide(intent, level=None, situation=None) -> AutonomyDecision(level, situation, risk_class, categories, may_execute, requires_confirmation, reasons)`

## Rules (in order)
1. Start at `level` or the configured default (2).
2. `auto execute` → level 3. `ask before send` → cap at 2. Preview mode → cap at 1.
3. Risk class = the tool's `risk_class` from the [tool registry](../data-models/tool-registry.md); no tool → `low`.
4. Categories = never-autonomous categories whose keywords appear anywhere in the raw command, content included ([autonomy policy](../data-models/autonomy-policy.md)).
5. `may_execute` = level ≥ 2 and mode is `execute` (dry run and preview never execute).
5b. **Situation**: at level 2 with `may_execute`, no `ask before send`, and the risk class in the state's `auto_risk` ([situation config](../data-models/situation-config.md)) → level 3, no confirmation. Applied before the hard rules ([ADR-0009](../decisions/0009-situation-policy.md)).
6. `requires_confirmation` = (level 2 and may_execute) **or** any category **or** risk class requires confirmation. Hard rules apply at **every** level, even when nothing runs, so a level-0/1 decision is never mistaken for "safe to auto-run".

## Connections
Part of the [brain](brain.md). Consumers must check `may_execute` first, then run the [confirmation loop](../flows/confirmation-loop.md) if `requires_confirmation`. Rationale: [ADR-0002](../decisions/0002-bounded-autonomy.md).
