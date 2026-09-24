---
type: Flow
title: Command pipeline
description: End-to-end path from a user command to a brief report.
timestamp: 2026-09-24T18:48:53Z
---

## Status
planned — built up across Phases 1–6.

## Steps
User → [interfaces](../modules/interfaces.md) → [context](../modules/context.md) signals → situation detection + intent resolution in the [brain](../modules/brain.md) → Prime delegates to [agents](../modules/agents.md) → [skills](../modules/skills.md) → [execution routing](../modules/execution.md) (autonomy + [confirmation loop](confirmation-loop.md)) → [adapters](../modules/adapters.md) → [tools](../modules/tools.md) → brain verifier → report.
