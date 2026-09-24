---
type: API
title: Command grammar
description: User command format: <action> <object> [target] [options].
timestamp: 2026-09-24T18:48:53Z
---

## Status
planned — parser in [Phase 1](../../phases/phase-01-brain.md). Vocabulary already loaded: [command vocabulary](../data-models/command-vocabulary.md).

## Grammar
`<action> <object> [target] [options]` — e.g. `send message to Rahul`, `create image maintenance banner use browser`.

## Rules
- Options can include a tool directive (`use gmail`), an autonomy modifier (`dry run`), or an agent directive (`plan then execute`).
- **If the tool or target is unclear → preview mode.** Never guess and execute.

Source doc: `docs/command_grammar.md`. Consumed by the [brain](../modules/brain.md).
