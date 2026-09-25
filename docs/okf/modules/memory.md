---
type: Module
title: Memory layer
description: Personal files outside the repo (profile, trust, logs) plus the nightly cycle.
timestamp: 2026-09-25T13:38:13Z
sources:
  - synkage/memory/__init__.py
  - synkage/memory/store.py
  - synkage/memory/night_cycle.py
  - scripts/nightly_update.py
---

## Status
built (Phase 7). Pattern promotion is not built.

## Files
| File | Role |
|---|---|
| `store.py` | `MemoryStore(config)`: `ensure()` creates the dir (0700) and missing files, never overwriting; load/save `UserProfile` and `RelationshipState` (trust, outcome counts, `last_night_cycle`, history capped at 90). Layout: [memory store](../data-models/memory-store.md) |
| `night_cycle.py` | `NightCycle(store).run(now) -> NightReport`: trust update and lossless compression. See [night cycle](../flows/night-cycle.md) |
| `scripts/nightly_update.py` | Runs the cycle once (cron/launchd), or `--schedule` for a daily apscheduler `BlockingScheduler` job (`night_cycle`, time from [memory config](../data-models/memory-config.md)) |

## Rules
Memory doesn't import brain, agents, skills, execution, adapters or tools (`tests/test_layer_boundaries.py`). The night cycle reads audit lines as raw JSON. The [CLI](cli.md) calls `ensure()` on every run ("created on first run"); tests use a temp memory dir via an autouse fixture. Decisions: [ADR-0010](../decisions/0010-memory-and-trust.md), [ADR-0004](../decisions/0004-local-file-memory.md).
