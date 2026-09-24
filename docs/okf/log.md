# OKF log

Newest first.

## 2026-09-24T19:40:06Z — Phase 5 (Tool control), automated part
- New: [ADR-0008](decisions/0008-macos-tool-control.md), [WhatsApp Web](services/whatsapp-web.md), [Gmail](services/gmail.md), [Apple Notes](services/apple-notes.md), [manual checks runbook](runbooks/phase5-manual-checks.md).
- Built: [tools](modules/tools.md). Updated: [adapters](modules/adapters.md) (handlers, draft/discard), [execution routing](flows/execution-routing.md) + [execution](modules/execution.md) (draft step), [CLI](modules/cli.md) (`login`, draft in `run`), [tool registry](data-models/tool-registry.md), [app preferences](data-models/app-preferences.md), [command vocabulary](data-models/command-vocabulary.md), [audit log](data-models/audit-log.md), [confirmation loop](flows/confirmation-loop.md), [local setup](runbooks/local-setup.md).

## 2026-09-24T19:27:24Z — Phase 4 (Routing)
- New: [execution routing](flows/execution-routing.md), [audit log](data-models/audit-log.md).
- Built: [adapters](modules/adapters.md), [execution](modules/execution.md) (action planner, router, audit).
- Updated: [CLI](modules/cli.md) (`run`; shell routes), [intent resolver](modules/intent-resolver.md) + [command grammar](apis/command-grammar.md) (safer option inside content → preview), [confirmation loop](flows/confirmation-loop.md), [tool registry](data-models/tool-registry.md), [config loader](modules/config-loader.md), [agents](modules/agents.md), [brain](modules/brain.md), [tools](modules/tools.md), [OpenClaw](services/openclaw-runtime.md), [command pipeline](flows/command-pipeline.md).

## 2026-09-24T19:17:25Z — Phase 3 (Skills)
- Built: [skills](modules/skills.md) (base class, registry with default-deny permissions, plan_steps, classify_intent, format_note).
- Updated: [agents](modules/agents.md) (planner/builder call skills via the registry), [autonomy policy](data-models/autonomy-policy.md) (`agent_skills`), [config loader](modules/config-loader.md), [CLI](modules/cli.md) (`skills`), [agent chain](flows/agent-chain.md), [agent artifact](data-models/agent-artifact.md), [command pipeline](flows/command-pipeline.md).

## 2026-09-24T19:11:34Z — Phase 2 (Agents)
- New: [agent artifact](data-models/agent-artifact.md), [agent chain](flows/agent-chain.md).
- Updated: [agents](modules/agents.md) (built), [brain](modules/brain.md) (`Prime.delegate`), [CLI](modules/cli.md) (`prepare`, shell prepares before confirming), [config loader](modules/config-loader.md) (`resolve_runs_dir`), [command pipeline](flows/command-pipeline.md).

## 2026-09-24T18:58:38Z — Phase 1 (Brain)
- New: [intent resolver](modules/intent-resolver.md), [autonomy guard](modules/autonomy-guard.md).
- Built: [confirmation loop](flows/confirmation-loop.md) (steps 1–3), [command grammar](apis/command-grammar.md).
- Updated: [brain](modules/brain.md), [execution](modules/execution.md), [CLI](modules/cli.md) (`parse`, `shell`), [command vocabulary](data-models/command-vocabulary.md) (verb rules, object types), [autonomy policy](data-models/autonomy-policy.md) (category keywords).

## 2026-09-24T18:48:53Z — Genesis + Phase 0
- Bundle created. Layer modules seeded (scaffolded packages), Phase 0 modules built: [CLI](modules/cli.md), [config loader](modules/config-loader.md), [logging](modules/logging.md).
- Data models for all config files; memory store planned.
- ADRs 0001–0007 recorded ([index](decisions/index.md)).
