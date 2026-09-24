---
type: Module
title: Brain layer
description: Decision engine: intent, situation, autonomy level, strategy, verification.
timestamp: 2026-09-24T18:48:53Z
sources:
  - synkage/brain/__init__.py
---

## Status
scaffolded — package exists; logic planned for [Phase 1](../../phases/phase-01-brain.md) and [Phase 6](../../phases/phase-06-situation.md).

## Responsibilities
- Resolve intent from a command (see [command grammar](../apis/command-grammar.md)).
- Classify situation state (rule-based — [ADR-0003](../decisions/0003-rule-based-situation-detection.md)).
- Decide autonomy level from confidence, situation, risk class, tool sensitivity, trust ([autonomy policy](../data-models/autonomy-policy.md)).
- Select execution strategy and delegate to [agents](agents.md).
- Verify results coming back from [adapters](adapters.md).

**Never executes tools directly** ([ADR-0001](../decisions/0001-layered-decision-execution-split.md)).

## Planned files
`prime.py`, `intent_resolver.py`, `situation_detector.py`, `priority_resolver.py`, `autonomy_guard.py`, `verifier.py` under `synkage/brain/`.

## Connections
Reads signals from [context](context.md). Uses `HARD_NEVER_AUTONOMOUS` from the [config loader](config-loader.md). Part of the [command pipeline](../flows/command-pipeline.md).
