---
type: Phase
title: Agent layer
description: Prime delegates a task to a specialist agent that returns a file artifact.
timestamp: 2026-09-24T18:48:00Z
tags: [phase]
---

## Status
done

## Goal
Prime delegates a task to a specialist agent that returns a file artifact.

## Scope
**In:** base_agent.py task contract, planner_agent, builder_agent, reporter_agent, file-based chaining.
**Out:** researcher and critic agents (later), skills registry, tool execution.

## Acceptance criteria
Tick in `phases.json` with evidence when met.
- [x] **ac-1** base_agent defines a typed task contract (input, output artifact path, status) — unit test passes  
  _Evidence:_ tests/test_base_agent.py (8 tests): AgentTask requires output; artifact written to task.output; inputs read from files; wrong agent / missing input / invalid input / exception -> status=failed, no output
- [x] **ac-2** planner, builder, reporter agents each produce an artifact file from a sample task — one test per agent  
  _Evidence:_ tests/test_agents.py::test_planner_produces_plan, ::test_builder_produces_action_draft, ::test_reporter_produces_report (+4 edge tests)
- [x] **ac-3** Chain planner → builder → reporter passes artifacts through files only — integration test passes  
  _Evidence:_ tests/test_delegation.py::test_full_chain_passes_artifacts_through_files (inputs chain 01->02->03); tests/test_agents.py::test_builder_uses_the_plan_file_not_its_own_plan; tests/test_layer_boundaries.py
- [x] **ac-4** Prime.delegate(intent) picks an agent and returns its artifact path — test passes  
  _Evidence:_ tests/test_delegation.py::test_delegate_returns_last_artifact_path, ::test_select_chain[7 cases], ::test_level_0_runs_no_agents, ::test_chain_stops_at_first_failure

## Depends on
[phase-01-brain](phase-01-brain.md)

## OKF concepts touched
- [modules/agents.md](../okf/modules/agents.md)
- [modules/brain.md](../okf/modules/brain.md)

## Notes
Done. Artifacts go to `runs/<run-id>/` (gitignored, `SYNKAGE_RUNS_DIR` overrides). Researcher and critic agents deferred (out of scope). Agents are rule-based until skills exist (Phase 3).

plan.md Phase 2 (Week 3).
