---
type: Decision
title: ADR-0005 External runtimes are adapters, not authorities
description: OpenClaw and similar runtimes plug in behind the adapter layer and the autonomy guard.
timestamp: 2026-09-24T18:48:53Z
tags: [adr, decision]
---

## Status
accepted (from spec)

## Context
README / architecture: OpenClaw handles runtime, channels, pipelines; Synkage keeps intent, situation, autonomy, safety.

## Decision
Every external runtime is reached through an [adapter](../modules/adapters.md). It cannot bypass the autonomy guard; all results go through the brain's verifier.

## Alternatives considered
- Hand whole tasks to OpenClaw — rejected: would bypass Synkage's safety model.

## Consequences
Runtimes are swappable and optional. Adapter must map each runtime's actions onto Synkage risk classes.

## Related
[OpenClaw runtime](../services/openclaw-runtime.md).
