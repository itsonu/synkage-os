---
type: API
title: Command grammar
description: User command format: <action> <object> [target] [options].
timestamp: 2026-09-24T19:27:24Z
sources:
  - synkage/brain/intent_resolver.py
---

## Status
built — parsed by the [intent resolver](../modules/intent-resolver.md). Vocabulary: [command vocabulary](../data-models/command-vocabulary.md).

## Grammar
`<action> <object> [target] [options]` — e.g. `send message to Rahul`, `create image maintenance banner use browser`.

## Rules
- Options can include a tool directive (`use gmail`), an autonomy modifier (`dry run`), or an agent directive (`plan then execute`).
- Text after the first `:` is message **content**; options inside it are ignored. Put options before the `:` (`send message to Raj dry run: hi`). A safer option at the very end of the content forces preview.
- **If the tool or target is unclear → preview mode.** Never guess and execute.

Source doc: `docs/command_grammar.md`. Consumed by the [brain](../modules/brain.md).
