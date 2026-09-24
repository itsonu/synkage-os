---
type: Module
title: Execution adapter layer
description: Replaceable backends that translate action requests into tool or runtime calls.
timestamp: 2026-09-24T19:27:24Z
sources:
  - synkage/adapters/__init__.py
  - synkage/adapters/tool_adapter_base.py
  - synkage/adapters/local_exec_adapter.py
  - synkage/adapters/openclaw_adapter.py
  - synkage/adapters/registry.py
---

## Status
in-progress — contract, `local_exec` (no controllers yet) and the `openclaw` stub were built in [Phase 4](../../phases/phase-04-routing.md). Real controllers come in [Phase 5](../../phases/phase-05-tool-control.md); the real OpenClaw adapter in [Phase 8](../../phases/phase-08-openclaw.md).

## Contract (`tool_adapter_base.py`)
- `ActionRequest` is the builder's `action_draft` body ([agent artifact](../data-models/agent-artifact.md)). It uses `extra="forbid"`, so builder/adapter drift fails loudly; `tests/test_adapters.py` checks that real builder drafts validate.
- `ToolAdapter.execute(request) -> ExecutionResult(status, adapter, tool, message, output)`.
- `ExecutionStatus` values: `success`, `failed`, `unavailable` (disabled tool, no controller, stub), `refused` (router), `dry_run`, `skipped` (nothing to execute).
- Adapters never decide autonomy. When `execute()` is called, the [router](../flows/execution-routing.md) has already enforced confirmation and safety.

## Adapters
| Name (= `adapter` in [tool registry](../data-models/tool-registry.md)) | Behaviour |
|---|---|
| `local_exec` | Dispatches to `CONTROLLERS[tool_id]` (empty until Phase 5 → `unavailable`). A controller exception becomes `failed` |
| `openclaw` | Stub: always `unavailable` |

`registry.ADAPTERS` maps each name to its class.

## Rules
Adapters don't import `synkage.brain`, `synkage.agents` or `synkage.execution` (`tests/test_layer_boundaries.py`).

## Connections
Called only by the [execution layer](execution.md). Drives [tools](tools.md) and the [OpenClaw runtime](../services/openclaw-runtime.md) ([ADR-0005](../decisions/0005-external-runtimes-as-adapters.md)).
