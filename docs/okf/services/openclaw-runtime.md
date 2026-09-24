---
type: Integration
title: OpenClaw runtime
description: Optional external agent runtime used as an execution substrate.
timestamp: 2026-09-24T18:48:53Z
---

## Status
planned — optional, [Phase 8](../../phases/phase-08-openclaw.md). Registered as `openclaw` (disabled) in the [tool registry](../data-models/tool-registry.md).

## Role
Handles agent runtime, channel execution, tool pipelines. Synkage keeps intent, situation, autonomy, and safety. Reached only through the [adapter layer](../modules/adapters.md) — [ADR-0005](../decisions/0005-external-runtimes-as-adapters.md).

## Unknowns
OpenClaw's API/contract is not described anywhere in the spec.
