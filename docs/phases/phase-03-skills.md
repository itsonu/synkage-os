---
type: Phase
title: Skills system
description: Agents invoke stateless, permission-gated skills through a registry.
timestamp: 2026-09-24T18:48:00Z
tags: [phase]
---

## Status
done

## Goal
Agents invoke stateless, permission-gated skills through a registry.

## Scope
**In:** base_skill.py, skill registry, permission gating, 3–5 skills: summarize, classify intent, plan steps, draft message, format note.
**Out:** Tool execution.

## Acceptance criteria
Tick in `phases.json` with evidence when met.
- [x] **ac-1** Skill registry lists registered skills and rejects duplicates — test passes  
  _Evidence:_ tests/test_skill_registry.py::test_lists_registered_skills, ::test_rejects_duplicate_names, ::test_register_after_init_rejects_duplicate (+ unknown skill, input/output validation)
- [x] **ac-2** Calling a skill the agent lacks permission for raises PermissionDenied — test passes  
  _Evidence:_ tests/test_skill_registry.py::test_permission_denied_for_unlisted_skill, ::test_unlisted_agent_is_denied_everything, ::test_permission_checked_before_input_validation, ::test_permission_config_names_real_agents_and_skills
- [x] **ac-3** At least 3 of the 5 MVP skills implemented, each with a passing unit test  
  _Evidence:_ 3 of 5 built: plan_steps, classify_intent, format_note — tests/test_skills.py (17 tests). summarize + draft_message deferred pending the LLM decision
- [x] **ac-4** An agent from Phase 2 invokes a skill only via the registry — test passes  
  _Evidence:_ tests/test_agents_use_skills.py (5 tests: planner calls go through the registry, planner output comes from the registered skill, planner fails with PermissionDenied when not allowed, builder formats notes via registry); tests/test_layer_boundaries.py::test_agents_reach_skills_only_through_the_registry

## Depends on
[phase-02-agents](phase-02-agents.md)

## OKF concepts touched
- [modules/skills.md](../okf/modules/skills.md)
- [modules/agents.md](../okf/modules/agents.md)
- [data-models/autonomy-policy.md](../okf/data-models/autonomy-policy.md)

## Notes
Done with 3 rule-based skills. **Deferred:** summarize and draft_message, pending the LLM-or-not decision (state.md open question 1). Permissions are per-agent allow-lists in `config/permissions.yaml` (`agent_skills`, default deny).

plan.md Phase 3 (Week 4). Blocked on the LLM-or-not question in state.md before building text skills.
