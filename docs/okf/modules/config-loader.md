---
type: Module
title: Config loader
description: Loads and validates every file in config/ into a typed SynkageConfig.
timestamp: 2026-09-24T19:17:25Z
sources:
  - synkage/config.py
---

## Status
built (Phase 0)

## Interface
- `load_config(config_dir=None) -> SynkageConfig`
- `resolve_config_dir()` — explicit arg > `SYNKAGE_CONFIG_DIR` (env or `.env`) > `<repo>/config`.
- `resolve_runs_dir()` — explicit arg > `SYNKAGE_RUNS_DIR` > `<repo>/runs` ([agent artifact](../data-models/agent-artifact.md) location).
- `ConfigError` — every failure; message names the file.
- `HARD_NEVER_AUTONOMOUS` — built-in safety categories.
- `tool_registry_json_schema()` — source for `config/schema/tool_registry.schema.json`.

## Validation rules
- All models `extra="forbid"`: unknown keys fail.
- Levels must be exactly 0–3; `default_level` must be one of them.
- Risk classes `high` and `critical` must exist and require confirmation.
- `never_autonomous` may add categories, never drop a built-in one ([ADR-0002](../decisions/0002-bounded-autonomy.md)).
- Every never-autonomous category has at least one `category_keywords` entry, and no keywords exist for unknown categories.
- Verbs are a map of `VerbRule {needs_target, needs_tool}`.
- `permissions.agent_skills` is an agent → skill-names map. Names are checked against the registry by `tests/test_skill_registry.py`, not at load time (config doesn't import the skills layer).
- Tool ids unique; every tool's `risk_class` exists.
- Every preferred tool and every `use <x>` directive points at a registered tool.

## Reads
[autonomy policy](../data-models/autonomy-policy.md), [command vocabulary](../data-models/command-vocabulary.md), [app preferences](../data-models/app-preferences.md), [tool registry](../data-models/tool-registry.md).

## Used by
[CLI](cli.md), [intent resolver](intent-resolver.md), [autonomy guard](autonomy-guard.md).
