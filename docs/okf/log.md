# OKF log

Newest first.

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
