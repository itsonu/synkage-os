---
type: Data Model
title: Agent artifact
description: JSON file each agent writes; the only channel between agents.
timestamp: 2026-09-24T19:11:34Z
sources:
  - synkage/agents/base_agent.py
---

## Status
built (Phase 2)

## Schema (`Artifact`)
| Field | Type | Notes |
|---|---|---|
| `agent` | str | Agent that wrote the file |
| `kind` | str | `plan`, `action_draft` or `report` |
| `task_id` | str | `<run-id>/<NN>-<agent>` |
| `created` | datetime (UTC) | |
| `inputs` | list[str] | Paths of the artifacts this one was built from |
| `summary` | str | One line for humans |
| `body` | object | Agent-specific (see [agents](../modules/agents.md)) |

## Location
`<runs dir>/<run-id>/NN-<agent>.json`. The runs dir is set by `SYNKAGE_RUNS_DIR` (defaults to `<repo>/runs`, which is gitignored) and resolved by `resolve_runs_dir()` in the [config loader](../modules/config-loader.md). The run id is `<UTC stamp>-<verb-object slug>-<6 hex>`.

## Unknowns
- Artifacts contain message text, and nothing cleans them up yet. Retention and location belong with the memory decision in [Phase 7](../../phases/phase-07-memory.md).
