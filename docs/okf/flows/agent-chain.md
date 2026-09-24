---
type: Flow
title: Agent chain
description: How Prime picks agents and chains them through files.
timestamp: 2026-09-24T19:27:36Z
sources:
  - synkage/brain/prime.py
---

## Status
built (Phase 2)

## Chain selection (`select_chain`)
| Condition | Chain |
|---|---|
| Level 0 (observe) | none; no run folder is created |
| Unknown verb, preview mode, level 1, or verb `plan` | planner → reporter |
| Otherwise (including dry run) | planner → builder → reporter |

`research then write` runs the full chain with a note that the researcher isn't built yet.

## Steps (`Prime.delegate`)
1. Make a run id and folder under the runs dir ([agent artifact](../data-models/agent-artifact.md)).
2. For each agent: build an `AgentTask` whose `inputs` are all earlier outputs and whose `output` is `NN-<agent>.json`, then run it.
3. Stop at the first `failed` result.
4. Return `DelegationResult(run_id, run_dir, chain, results, notes)`. `.artifact` is the last agent's file, and only when every agent succeeded. `.output_of(agent)` returns one agent's file (the CLI uses `output_of("builder")` to find the draft it routes).

Delegation only prepares (plans, drafts, reports). It runs at levels 1–3 and never needs confirmation, because nothing is executed. Confirmation comes afterwards, in the [confirmation loop](confirmation-loop.md).

Prime creates one [skill registry](../modules/skills.md) and passes it to every agent in the chain.

## Connections
Called from the [brain](../modules/brain.md). Uses the [agents](../modules/agents.md). Part of the [command pipeline](command-pipeline.md).
