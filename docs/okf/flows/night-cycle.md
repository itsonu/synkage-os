---
type: Flow
title: Night cycle
description: Daily job that updates trust from logged outcomes and compresses old audit records.
timestamp: 2026-09-25T13:38:13Z
sources:
  - synkage/memory/night_cycle.py
  - scripts/nightly_update.py
---

## Status
built (Phase 7). Not built: pattern promotion.

## Steps (`NightCycle.run`)
1. `ensure()` memory; take an **exclusive flock** on the [audit log](../data-models/audit-log.md), the same lock `AuditLog.append` takes, so nothing appended mid-cycle is lost (a real-thread race test proves it and fails without the lock).
2. **Trust:** `trust = neutral + (trust − neutral) × (1 − decay_per_day)^days_since_last_cycle` (first run: 1 day), then add a delta for each record logged after the last cycle and not in the future:

   | Record | Outcome |
   |---|---|
   | status `failed` | failed |
   | `confirmed: false` | declined |
   | `confirmed: true` and `success` | confirmed_success |
   | anything else (auto-run, dry run, unavailable) | no signal |

   The result is clamped to [0, 1]. Outcome counts accumulate, and a history point is appended.
3. **Compress** records older than `retention_days`: per-day summaries are merged into `log_summaries.json`; raw lines are appended to `archive/logs-YYYY-MM.jsonl.gz`; `logs.jsonl` is rewritten with the rest. Unparseable lines are always kept. If nothing is old, the file is untouched.
4. Save `last_night_cycle` and return a `NightReport`.

## Running it
- Once: `python scripts/nightly_update.py` (exit 0; for cron/launchd).
- Daemon: `python scripts/nightly_update.py --schedule` (apscheduler, daily at [memory config](../data-models/memory-config.md) `schedule`).

## Connections
Part of the [memory layer](../modules/memory.md); writes the [memory store](../data-models/memory-store.md).
