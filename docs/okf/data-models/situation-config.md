---
type: Data Model
title: Situation config
description: Signal thresholds, keywords, quiet hours and per-state autonomy policy.
timestamp: 2026-09-25T13:30:46Z
sources:
  - config/situation.yaml
---

## Status
built (Phase 6)

## Fields (`SituationConfig`)
| Field | Default | Used by |
|---|---|---|
| `idle_after_seconds` | 300 | detector rule 4 |
| `focus_apps` | Code, VS Code, Xcode, PyCharm, IntelliJ, Terminal, iTerm2 | rule 5 (frontmost macOS app) |
| `urgent_keywords` / `emergency_keywords` | urgent, asap, immediately, right now / emergency, sos | rules 2–3 (whole words, before `:`) |
| `quiet_hours` | 23:00–07:00 (HH:MM, may wrap midnight) | rule 6 |
| `states.<state>.auto_risk` | focused/urgent/emergency: `[low]`; idle/normal: `[]` | [autonomy guard](../modules/autonomy-guard.md) |

## Validation ([config loader](../modules/config-loader.md))
- `states` must be exactly the five states.
- `auto_risk` entries must be known risk classes that **don't** require confirmation, so high/critical are rejected.
- Quiet hours must be `HH:MM`.

Rationale: [ADR-0009](../decisions/0009-situation-policy.md). Read by the [situation detector](../modules/situation-detector.md).
