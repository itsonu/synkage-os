---
type: Module
title: Agent layer
description: Specialist reasoning workers that chain through files and invoke skills.
timestamp: 2026-09-24T19:11:34Z
sources:
  - synkage/agents/__init__.py
  - synkage/agents/base_agent.py
  - synkage/agents/planner_agent.py
  - synkage/agents/builder_agent.py
  - synkage/agents/reporter_agent.py
  - synkage/agents/registry.py
---

## Status
in-progress — contract plus planner, builder, reporter built in [Phase 2](../../phases/phase-02-agents.md). Researcher and critic not built. Skills arrive in [Phase 3](../../phases/phase-03-skills.md).

## Contract (`base_agent.py`)
- `AgentTask(id, agent, intent, decision, inputs: list[Path], output: Path)`: the only thing an agent receives.
- `BaseAgent.run(task) -> AgentResult(task_id, agent, status: done|failed, output, error)`. It reads `inputs` from disk, calls the subclass's `produce()`, and writes an [agent artifact](../data-models/agent-artifact.md) to `output` atomically.
- Failures never raise. A wrong agent name, a missing or invalid input, or an exception in `produce()` all become `status=failed` with an `error`, and no output file is written.
- Subclasses set `name` and `kind`, then implement `produce(task, inputs) -> (summary, body)`.

## Agents
| Agent | Artifact `kind` | Does |
|---|---|---|
| planner | `plan` | Rule-based step templates per verb; `blocked` lists the reasons for a preview |
| builder | `action_draft` | Needs exactly one `plan` input; builds the payload the router will execute in Phase 4 (tool, adapter, target, content, steps, `ready`, `missing`) |
| reporter | `report` | Writes a brief text: ready or not, confirmation needed, safety flags, steps, "Nothing was executed" |

`registry.AGENTS` maps each name to its class. [Prime](brain.md) picks the chain; see [agent chain](../flows/agent-chain.md).

## Rules
- Earlier work is read **only from input files**. Tests prove this: a hand-edited plan file changes the builder's output.
- Agents never import `synkage.tools`, `synkage.adapters` or `synkage.execution`. `tests/test_layer_boundaries.py` enforces this.
- Agents never control [tools](tools.md) directly.

## Connections
Delegated to by the [brain](brain.md). Step in the [command pipeline](../flows/command-pipeline.md).
