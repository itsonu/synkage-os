---
type: Module
title: Situation detector
description: Rule-based classification of signals into idle, normal, focused, urgent or emergency.
timestamp: 2026-09-25T13:30:46Z
sources:
  - synkage/brain/situation_detector.py
---

## Status
built (Phase 6)

## Interface
`SituationDetector(config.situation).classify(signals) -> Situation(state, reasons)`. `Prime.situation(command)` collects [signals](context.md) and classifies them; `Prime.handle` passes the result to the [autonomy guard](autonomy-guard.md) and returns it on `PrimeResult.situation`.

## Rules (first match wins)
1. Explicit override (`--situation`) → that state
2. Emergency keyword in the command (before `:`) → emergency
3. Urgent keyword → urgent
4. Idle ≥ `idle_after_seconds` → idle
5. Frontmost app is a focus app (case-insensitive) → focused
6. Quiet hours **and** no activity data at all → idle
7. Otherwise → normal

Unknown signals (`None`) never trigger a rule, so missing data falls through to normal ([ADR-0003](../decisions/0003-rule-based-situation-detection.md)).

## Gotchas
While a command is being typed, idle time is about 0, so the idle rule mostly matters for future proactive flows. What each state does to autonomy: [ADR-0009](../decisions/0009-situation-policy.md).

## Connections
Part of the [brain](brain.md). Reads the [situation config](../data-models/situation-config.md).
