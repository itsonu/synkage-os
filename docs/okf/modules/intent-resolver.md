---
type: Module
title: Intent resolver
description: Rule-based parser turning a command string into a structured Intent.
timestamp: 2026-09-24T19:27:24Z
sources:
  - synkage/brain/intent_resolver.py
---

## Status
built (Phase 1)

## Interface
`IntentResolver(config).resolve(text) -> Intent`

| Intent field | Meaning |
|---|---|
| `verb`, `object`, `target` | `<action> <object> [target]` |
| `details` | Extra words (e.g. `meeting at 4pm` in `save note meeting at 4pm`) |
| `content` | Text after the first `:` |
| `tool`, `tool_source` | Tool id and how it was found: `directive` (`use gmail`) > `mention` (`whatsapp message`) > `preference` (object type → [app preferences](../data-models/app-preferences.md)) |
| `modifier` | `preview` / `confirm` / `auto` / `dry_run` |
| `agent_directive` | e.g. `plan then execute` |
| `mode` | `execute` / `preview` / `dry_run` |
| `unclear` | Reasons the command couldn't be pinned down. Non-empty ⇒ `mode=preview` |

## Algorithm
1. Split off content at the first `:` (options inside content are ignored).
2. Strip autonomy modifiers, then agent directives, then `use <tool>` from the head. An unknown `use X` is recorded as unclear, never dropped.
3. First word = verb (must be in [command vocabulary](../data-models/command-vocabulary.md); typo → rapidfuzz "did you mean" hint, still preview).
4. Inline tool mention removed from the phrase (plus a preceding `on`/`via`/`with`), except for `open`, where the tool *is* the object.
5. Target verbs (`send`, `reply`): split on `to`, else first word = object, rest = target. Other verbs: `X as <object>`, or known object noun + details, or the whole phrase as object.
6. No tool yet → preferred tool for the object's task type (skipped if the user named an unknown tool).
7. Missing required target/tool (per verb rule) → unclear → preview.

## Options inside message text
Options after `:` never apply. A **safer** modifier (`dry run`, `preview only`, `ask before send`) at the *end* of the content forces preview with the hint "put options before ':'", because running normally would surprise the user. `auto execute` in content is silently ignored. A modifier in the middle of the content ("can we do a dry run tomorrow") is just text.

## Gotchas
- `use` anywhere in the head starts a tool directive, so `summarize how to use docker` goes to preview (unknown tool 'docker'). Safe direction; revisit if it annoys.
- Object keeps the user's casing; verb is lowercased.

## Connections
Part of the [brain](brain.md); output feeds the [autonomy guard](autonomy-guard.md). Implements the [command grammar](../apis/command-grammar.md).
