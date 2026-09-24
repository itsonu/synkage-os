---
type: Module
title: Execution adapter layer
description: Replaceable backends that translate tasks into tool or runtime calls.
timestamp: 2026-09-24T18:48:53Z
sources:
  - synkage/adapters/__init__.py
---

## Status
scaffolded — planned for [Phase 4](../../phases/phase-04-routing.md) and [Phase 8](../../phases/phase-08-openclaw.md).

## Responsibilities
Translate tasks into backend calls, normalize results, enforce safety boundaries. Each [tool registry](../data-models/tool-registry.md) entry names the adapter that drives it (`local_exec`, `openclaw`).

## Planned files
`tool_adapter_base.py`, `local_exec_adapter.py`, `openclaw_adapter.py`.

## Connections
Drives [tools](tools.md) and the [OpenClaw runtime](../services/openclaw-runtime.md). Cannot bypass the autonomy guard ([ADR-0005](../decisions/0005-external-runtimes-as-adapters.md)).
