---
type: Module
title: Brain layer
description: Decision engine: intent, situation, autonomy level, strategy, verification.
timestamp: 2026-09-24T19:11:34Z
sources:
  - synkage/brain/__init__.py
  - synkage/brain/prime.py
  - synkage/brain/intent_resolver.py
  - synkage/brain/autonomy_guard.py
---

## Status
in-progress — intent resolver and autonomy guard built in [Phase 1](../../phases/phase-01-brain.md); Prime delegation built in [Phase 2](../../phases/phase-02-agents.md). Situation detector ([Phase 6](../../phases/phase-06-situation.md)), priority resolver and verifier are still planned.

## Responsibilities
- Resolve intent from a command (see [command grammar](../apis/command-grammar.md)).
- Classify situation state (rule-based — [ADR-0003](../decisions/0003-rule-based-situation-detection.md)).
- Decide autonomy level from confidence, situation, risk class, tool sensitivity, trust ([autonomy policy](../data-models/autonomy-policy.md)).
- Select execution strategy and delegate to [agents](agents.md).
- Verify results coming back from [adapters](adapters.md).

**Never executes tools directly** ([ADR-0001](../decisions/0001-layered-decision-execution-split.md)).

## Files
| File | Status |
|---|---|
| `prime.py` | built — `Prime.handle(text) -> PrimeResult(intent, decision)`; `Prime.delegate(result) -> DelegationResult` runs the [agent chain](../flows/agent-chain.md) |
| `intent_resolver.py` | built — see [intent resolver](intent-resolver.md) |
| `autonomy_guard.py` | built — see [autonomy guard](autonomy-guard.md) |
| `situation_detector.py`, `priority_resolver.py`, `verifier.py` | planned |

## Connections
Reads signals from [context](context.md). Uses `HARD_NEVER_AUTONOMOUS` from the [config loader](config-loader.md). Part of the [command pipeline](../flows/command-pipeline.md).
