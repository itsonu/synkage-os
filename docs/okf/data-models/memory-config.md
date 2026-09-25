---
type: Data Model
title: Memory config
description: Retention, trust deltas and decay, and the night-cycle schedule.
timestamp: 2026-09-25T13:38:13Z
sources:
  - config/memory.yaml
---

## Status
built (Phase 7)

## Fields (`MemoryConfig`)
| Field | Default | Validation |
|---|---|---|
| `retention_days` | 30 | ≥ 1 |
| `trust.neutral` | 0.5 | 0–1 |
| `trust.success` / `declined` / `failed` | +0.02 / −0.03 / −0.05 | success 0…0.5; others −0.5…0 |
| `trust.decay_per_day` | 0.1 | 0–1 |
| `schedule.hour` / `minute` | 3 / 17 | valid clock time |

Loaded by the [config loader](../modules/config-loader.md). Used by the [night cycle](../flows/night-cycle.md). Rationale: [ADR-0010](../decisions/0010-memory-and-trust.md).
