---
type: Phase
title: Skills system
description: Agents invoke stateless, permission-gated skills through a registry.
timestamp: 2026-09-24T18:48:00Z
tags: [phase]
---

## Status
todo

## Goal
Agents invoke stateless, permission-gated skills through a registry.

## Scope
**In:** base_skill.py, skill registry, permission gating, 3–5 skills: summarize, classify intent, plan steps, draft message, format note.
**Out:** Tool execution.

## Acceptance criteria
Tick in `phases.json` with evidence when met.
- [ ] **ac-1** Skill registry lists registered skills and rejects duplicates — test passes
- [ ] **ac-2** Calling a skill the agent lacks permission for raises PermissionDenied — test passes
- [ ] **ac-3** At least 3 of the 5 MVP skills implemented, each with a passing unit test
- [ ] **ac-4** An agent from Phase 2 invokes a skill only via the registry — test passes

## Depends on
[phase-02-agents](phase-02-agents.md)

## OKF concepts touched
- [modules/skills.md](../okf/modules/skills.md)
- [modules/agents.md](../okf/modules/agents.md)
- [data-models/autonomy-policy.md](../okf/data-models/autonomy-policy.md)

## Notes
plan.md Phase 3 (Week 4). Blocked on the LLM-or-not question in state.md before building text skills.
