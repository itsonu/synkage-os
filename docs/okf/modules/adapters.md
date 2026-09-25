---
type: Module
title: Execution adapter layer
description: Replaceable backends that translate action requests into tool or runtime calls.
timestamp: 2026-09-25T13:40:01Z
sources:
  - synkage/adapters/__init__.py
  - synkage/adapters/tool_adapter_base.py
  - synkage/adapters/local_exec_adapter.py
  - synkage/adapters/openclaw_adapter.py
  - synkage/adapters/registry.py
---

## Status
in-progress — contract and `openclaw` stub (Phase 4); `local_exec` handlers for WhatsApp, Gmail and Apple Notes ([Phase 5](../../phases/phase-05-tool-control.md)). The real OpenClaw adapter ([Phase 8](../../phases/phase-08-openclaw.md)) is **deferred**; the stub stays.

## Contract (`tool_adapter_base.py`)
- `ActionRequest` is the builder's `action_draft` body ([agent artifact](../data-models/agent-artifact.md)). It uses `extra="forbid"`, so builder/adapter drift fails loudly; `tests/test_adapters.py` checks that real builder drafts validate.
- `ToolAdapter.execute(request) -> ExecutionResult(status, adapter, tool, message, output)`.
- `ExecutionStatus` values: `success`, `failed`, `unavailable` (disabled tool, no controller, stub), `refused` (router), `dry_run`, `skipped` (nothing to execute).
- Optional draft step: `supports_draft(tool)`, `draft(request)` → `drafted`, `discard(request)` (best effort). The router uses these to stage an action before confirmation.
- Adapters never decide autonomy. When `execute()` is called, the [router](../flows/execution-routing.md) has already enforced confirmation and safety.

## Adapters
| Name (= `adapter` in [tool registry](../data-models/tool-registry.md)) | Behaviour |
|---|---|
| `local_exec` | Dispatches to `HANDLERS[tool_id]`, which translate requests into [tool](tools.md) calls: `WhatsAppHandler` (draft/send/discard; needs a target and text), `GmailHandler` (drafts only), `AppleNotesHandler` (save; uses the builder's `note`). No handler → `unavailable`; an exception → `failed`. One lazily opened `shared_session()`; `open_login_pages()` backs `synkage login` |
| `openclaw` | Stub: always `unavailable` |

`registry.ADAPTERS` maps each name to its class.

## Rules
Adapters don't import `synkage.brain`, `synkage.agents` or `synkage.execution` (`tests/test_layer_boundaries.py`).

## Connections
Called only by the [execution layer](execution.md). Drives [tools](tools.md) and the [OpenClaw runtime](../services/openclaw-runtime.md) ([ADR-0005](../decisions/0005-external-runtimes-as-adapters.md)).
