---
type: Decision
title: ADR-0001 Separate decision from execution
description: Strict layers; the brain decides, only adapters and tools act.
timestamp: 2026-09-24T18:48:53Z
tags: [adr, decision]
---

## Status
accepted (from spec)

## Context
`docs/architecture.md`: Synkage is a meta-orchestrator over local tools, browser automation, and external runtimes. It must stay safe and swappable.

## Decision
Eight layers with hard boundaries: interfaces → context → brain → agents → skills → execution routing → adapters → tools. Brain never executes tools; agents and skills never control tools; tools and interfaces hold no decision logic.

## Alternatives considered
- Single agent loop calling tools directly — rejected: no single place to enforce autonomy; backends not swappable.

## Consequences
More modules and contracts up front. Autonomy can be enforced in one place ([execution](../modules/execution.md)). Backends are replaceable.

## Related
[brain](../modules/brain.md), [execution](../modules/execution.md), [adapters](../modules/adapters.md), [command pipeline](../flows/command-pipeline.md).
