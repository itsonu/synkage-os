---
type: Data Model
title: Command vocabulary
description: Verbs, tool directives, autonomy modifiers, agent directives for command parsing.
timestamp: 2026-09-24T18:48:53Z
sources:
  - config/command_aliases.yaml
---

## Status
built (Phase 0) — loaded only; parsed by the intent resolver in [Phase 1](../../phases/phase-01-brain.md).

## Contents
- `verbs` — send, reply, create, save, open, find, summarize, plan, generate, execute.
- `tool_directives` — phrase after `use` → tool id in the [tool registry](tool-registry.md).
- `autonomy_modifiers` — `preview only`, `ask before send`, `auto execute`, `dry run`.
- `agent_directives` — `research then write`, `plan then execute`, `chain agents`.

Grammar: [command grammar](../apis/command-grammar.md).
