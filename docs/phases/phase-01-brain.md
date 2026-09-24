---
type: Phase
title: Brain layer
description: Commands parse into structured intents and the autonomy guard decides when confirmation is needed.
timestamp: 2026-09-24T18:48:00Z
tags: [phase]
---

## Status
todo

## Goal
Commands parse into structured intents and the autonomy guard decides when confirmation is needed.

## Scope
**In:** Command parser, intent_resolver.py, prime.py skeleton, autonomy_guard.py, confirmation loop, interactive CLI loop.
**Out:** Agents, skills, adapters, real execution, situation signals (use a fixed 'normal' state).

## Acceptance criteria
Tick in `phases.json` with evidence when met.
- [ ] **ac-1** 'send message to Rahul' parses to Intent(verb=send, object=message, target=Rahul) — unit test passes
- [ ] **ac-2** 'use gmail' resolves to tool id gmail via command_aliases.yaml; 'dry run' / 'preview only' / 'ask before send' / 'auto execute' set the intent's autonomy modifier — unit tests pass
- [ ] **ac-3** A command with unclear tool or target yields mode=preview (never execute) — unit test passes
- [ ] **ac-4** autonomy_guard returns requires_confirmation=True for every never_autonomous category and for high/critical risk at every level — parametrised test passes
- [ ] **ac-5** Confirmation loop shows plan + tool target and proceeds only on explicit 'yes' — test with scripted input covers yes/no/empty
- [ ] **ac-6** Interactive CLI loop (prompt-toolkit) reads a command and prints the parsed intent and required autonomy — CliRunner/scripted-input test passes

## Depends on
[phase-00-foundation](phase-00-foundation.md)

## OKF concepts touched
- [modules/brain.md](../okf/modules/brain.md)
- [modules/execution.md](../okf/modules/execution.md)
- [modules/interfaces.md](../okf/modules/interfaces.md)
- [apis/command-grammar.md](../okf/apis/command-grammar.md)
- [flows/confirmation-loop.md](../okf/flows/confirmation-loop.md)

## Notes
plan.md Phase 1 (Week 2). Exit: system parses commands into structured intents.
