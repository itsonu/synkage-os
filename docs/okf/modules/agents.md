---
type: Module
title: Agent layer
description: Specialist reasoning workers that chain through files and invoke skills.
timestamp: 2026-09-24T18:48:53Z
sources:
  - synkage/agents/__init__.py
---

## Status
scaffolded — logic planned for [Phase 2](../../phases/phase-02-agents.md).

## Responsibilities
Planner, researcher, builder, critic, reporter agents. Produce structured artifacts, chain tasks through **files**, call [skills](skills.md). Never control [tools](tools.md) directly.

## Planned files
`base_agent.py`, `planner_agent.py`, `researcher_agent.py`, `builder_agent.py`, `critic_agent.py`, `reporter_agent.py`.

## Connections
Delegated to by the [brain](brain.md). Step in the [command pipeline](../flows/command-pipeline.md).
