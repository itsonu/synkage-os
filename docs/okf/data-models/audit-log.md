---
type: Data Model
title: Audit log
description: Append-only JSONL record of every routed action.
timestamp: 2026-09-24T19:40:06Z
sources:
  - synkage/execution/audit.py
---

## Status
built (Phase 4)

## Location
`logs.jsonl` at the repo root (gitignored). `SYNKAGE_AUDIT_LOG` overrides it; the path is resolved by `resolve_audit_log()` in the [config loader](../modules/config-loader.md). Tests use a temp file via an autouse fixture.

## Record (`AuditRecord`, one JSON object per line)
| Field | Notes |
|---|---|
| `ts` | UTC |
| `run_id` | Links to `runs/<run-id>/` ([agent artifact](agent-artifact.md)) |
| `intent` | `raw`, `verb`, `object`, `target`, `mode` |
| `tool`, `adapter` | As planned by the router (registry adapter) |
| `autonomy_level` | From the decision |
| `risk_class`, `categories` | **As enforced by the router** (re-derived), not as claimed upstream |
| `confirmation` | `{required, confirmed}`; `confirmed` is null when never asked |
| `result` | `{status, message}`; `drafted` records a pre-confirmation draft |

The fields match `docs/autonomy_safety.md` (intent, tool, autonomy level, confirmation state, result). The log is only appended to; nothing rewrites it.

## Unknowns
- `intent.raw` includes message text. Retention and location move with the memory decision in [Phase 7](../../phases/phase-07-memory.md), where the spec's `memory/logs.json` lives.
