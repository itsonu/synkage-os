---
type: Decision
title: ADR-0003 Rule-based situation detection
description: Situation states come from signal rules, not a model.
timestamp: 2026-09-24T18:48:53Z
tags: [adr, decision]
---

## Status
accepted (from spec)

## Context
`docs/architecture.md`: "Situation detection is signal-driven, not model-driven." Must stay CPU-friendly.

## Decision
Classify Idle / Normal / Focused / Urgent / Emergency with explicit rules over [context](../modules/context.md) signals. The state adjusts autonomy thresholds, confirmation, speed, and interruption policy.

## Alternatives considered
- ML classifier — rejected: heavy, opaque, conflicts with "explainable".

## Consequences
Explainable and testable. Rules need tuning by hand.

## Related
[brain](../modules/brain.md), [Phase 6](../../phases/phase-06-situation.md).
