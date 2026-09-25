---
type: Data Model
title: Memory store
description: Personal files in ~/.synkage/memory — profile, relationship/trust, audit log, summaries, archive.
timestamp: 2026-09-25T13:38:13Z
sources:
  - synkage/memory/store.py
---

## Status
built (Phase 7). Location decided: `~/.synkage/memory/` ([ADR-0010](../decisions/0010-memory-and-trust.md)).

## Layout
| File | Contents |
|---|---|
| `user_profile.json` | `created`, `name`, `preferences` (grows later) |
| `relationship_state.json` | `trust` (0–1), `outcomes {confirmed_success, declined, failed}`, `last_night_cycle`, `history [{at, trust}]` (last 90) |
| `logs.jsonl` | [audit log](audit-log.md) |
| `log_summaries.json` | `{"YYYY-MM-DD": {total, by_status, by_tool, by_verb}}`, made by the [night cycle](../flows/night-cycle.md) |
| `archive/logs-YYYY-MM.jsonl.gz` | Raw audit lines the night cycle compressed (gzip members appended) |

The directory is created 0700 and holds message text. `SYNKAGE_MEMORY_DIR` overrides the location. Writes are atomic (temp file + rename).

## Connections
Written by the [memory layer](../modules/memory.md). Read by the [CLI](../modules/cli.md) `status` (trust, last cycle).
