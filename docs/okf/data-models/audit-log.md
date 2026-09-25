---
type: Data Model
title: Audit log
description: Append-only JSONL record of every routed action.
timestamp: 2026-09-25T13:38:13Z
sources:
  - synkage/execution/audit.py
---

## Status
built (Phase 4)

## Location
`<memory dir>/logs.jsonl`, i.e. `~/.synkage/memory/logs.jsonl` since Phase 7 (before that it was the repo root). `SYNKAGE_AUDIT_LOG` overrides it; the path is resolved by `resolve_audit_log()` in the [config loader](../modules/config-loader.md). Tests use a temp file via an autouse fixture. Part of the [memory store](memory-store.md).

## Record (`AuditRecord`, one JSON object per line)
| Field | Notes |
|---|---|
| `ts` | UTC |
| `run_id` | Links to `runs/<run-id>/` ([agent artifact](agent-artifact.md)) |
| `intent` | `raw`, `verb`, `object`, `target`, `mode` |
| `tool`, `adapter` | As planned by the router (registry adapter) |
| `autonomy_level` | From the decision |
| `situation` | State at decision time; explains a low-risk action that skipped confirmation (Phase 6) |
| `risk_class`, `categories` | **As enforced by the router** (re-derived), not as claimed upstream |
| `confirmation` | `{required, confirmed}`; `confirmed` is null when never asked |
| `result` | `{status, message}`; `drafted` records a pre-confirmation draft |

The fields match `docs/autonomy_safety.md` (intent, tool, autonomy level, confirmation state, result). `AuditLog.append` takes an exclusive flock. The **only** rewriter is the [night cycle](../flows/night-cycle.md), which moves records older than `retention_days` into daily summaries and a gzip archive (lossless) under the same lock.

## Unknowns
- None left from Phase 4: location and retention were decided in Phase 7 ([ADR-0010](../decisions/0010-memory-and-trust.md)).
