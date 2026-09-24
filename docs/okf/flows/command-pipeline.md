---
type: Flow
title: Command pipeline
description: End-to-end path from a user command to a brief report.
timestamp: 2026-09-24T19:17:25Z
---

## Status
in-progress — intent resolution, autonomy decision and confirmation (Phase 1) and [agent chain](agent-chain.md) delegation (Phase 2) work. [Skills](../modules/skills.md) (Phase 3) are called by agents via the registry. Routing and tools are still planned.

## Steps
User → [interfaces](../modules/interfaces.md) → [context](../modules/context.md) signals → situation detection + intent resolution in the [brain](../modules/brain.md) → Prime delegates to [agents](../modules/agents.md) → [skills](../modules/skills.md) → [execution routing](../modules/execution.md) (autonomy + [confirmation loop](confirmation-loop.md)) → [adapters](../modules/adapters.md) → [tools](../modules/tools.md) → brain verifier → report.
