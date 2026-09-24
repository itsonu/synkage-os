---
type: Flow
title: Confirmation loop
description: Gate for actions that need explicit user consent.
timestamp: 2026-09-24T19:27:24Z
sources:
  - synkage/execution/confirmation_loop.py
---

## Status
built. Steps 1–3 since Phase 1; steps 4–5 (execute, log) via the [execution router](execution-routing.md) since Phase 4. A `no` is routed too, so it is refused **and audited**.

## Steps
1. Show plan. 2. Show tool target. 3. Require explicit confirm. 4. Execute. 5. Log result.

Applies to high/critical risk and all never-autonomous categories ([autonomy policy](../data-models/autonomy-policy.md)). Owned by [execution](../modules/execution.md); prompt rendered by [interfaces](../modules/interfaces.md), which inject `ask`/`show`.

Only the exact word `yes` (case-insensitive, trimmed) confirms. `y`, `ok`, empty, EOF, Ctrl-C all cancel. Runs only when the [autonomy guard](../modules/autonomy-guard.md) says `may_execute and requires_confirmation`.
