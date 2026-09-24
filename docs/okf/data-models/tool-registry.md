---
type: Data Model
title: Tool registry
description: Registered tools, their kind, execution adapter, risk class, and enabled flag.
timestamp: 2026-09-24T19:27:24Z
sources:
  - config/tool_registry.json
  - config/schema/tool_registry.schema.json
---

## Status
built (Phase 0) — all tools `enabled: false` until their controllers exist ([Phase 5](../../phases/phase-05-tool-control.md)).

## Schema
| Field | Type | Notes |
|---|---|---|
| `id` | string `^[a-z][a-z0-9_]*$` | unique |
| `name` | string | display name |
| `kind` | `browser` \| `desktop` \| `runtime` | |
| `adapter` | string | [adapter](../modules/adapters.md) that drives it, e.g. `local_exec`, `openclaw` |
| `risk_class` | string | key in [autonomy policy](autonomy-policy.md) risk classes |
| `enabled` | bool | default false |
| `notes` | string | free text |

Top level: `$schema`, `version`, `tools[]`. Validated by the [config loader](../modules/config-loader.md). The JSON Schema file is **generated** — see [runbook](../runbooks/change-config-schema.md).

## Enforced by the router
- `adapter` picks the adapter; the draft's adapter is ignored.
- `enabled: false` → the router returns `unavailable` and never calls the adapter.
- `risk_class` drives confirmation.
See [execution routing](../flows/execution-routing.md).

## Seeded tools
browser, whatsapp_web, gmail, sticky_notes, vscode, openclaw.
