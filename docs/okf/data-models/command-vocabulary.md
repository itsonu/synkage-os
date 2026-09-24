---
type: Data Model
title: Command vocabulary
description: Verbs, tool directives, autonomy modifiers, agent directives for command parsing.
timestamp: 2026-09-24T18:58:38Z
sources:
  - config/command_aliases.yaml
---

## Status
built — used by the [intent resolver](../modules/intent-resolver.md) (Phase 1).

## Contents
- `verbs` — map of verb → `{needs_target, needs_tool}`. send/reply need both; create/save/open/execute need a tool; find/summarize/plan/generate need neither. *(Requirements inferred from README examples.)*
- `object_types` — object noun → task type in [app preferences](app-preferences.md) (message → messaging, email → email, note → notes…).
- `tool_directives` — phrase after `use` → tool id in the [tool registry](tool-registry.md).
- `autonomy_modifiers` — `preview only`, `ask before send`, `auto execute`, `dry run`.
- `agent_directives` — `research then write`, `plan then execute`, `chain agents`.

Grammar: [command grammar](../apis/command-grammar.md).
