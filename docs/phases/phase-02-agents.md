---
type: Phase
title: Agent layer
description: Prime delegates a task to a specialist agent that returns a file artifact.
timestamp: 2026-09-24T18:48:00Z
tags: [phase]
---

## Status
todo

## Goal
Prime delegates a task to a specialist agent that returns a file artifact.

## Scope
**In:** base_agent.py task contract, planner_agent, builder_agent, reporter_agent, file-based chaining.
**Out:** researcher and critic agents (later), skills registry, tool execution.

## Acceptance criteria
Tick in `phases.json` with evidence when met.
- [ ] **ac-1** base_agent defines a typed task contract (input, output artifact path, status) — unit test passes
- [ ] **ac-2** planner, builder, reporter agents each produce an artifact file from a sample task — one test per agent
- [ ] **ac-3** Chain planner → builder → reporter passes artifacts through files only — integration test passes
- [ ] **ac-4** Prime.delegate(intent) picks an agent and returns its artifact path — test passes

## Depends on
[phase-01-brain](phase-01-brain.md)

## OKF concepts touched
- [modules/agents.md](../okf/modules/agents.md)
- [modules/brain.md](../okf/modules/brain.md)

## Notes
plan.md Phase 2 (Week 3).
