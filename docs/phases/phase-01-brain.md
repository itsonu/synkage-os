---
type: Phase
title: Brain layer
description: Commands parse into structured intents and the autonomy guard decides when confirmation is needed.
timestamp: 2026-09-24T18:48:00Z
tags: [phase]
---

## Status
done

## Goal
Commands parse into structured intents and the autonomy guard decides when confirmation is needed.

## Scope
**In:** Command parser, intent_resolver.py, prime.py skeleton, autonomy_guard.py, confirmation loop, interactive CLI loop.
**Out:** Agents, skills, adapters, real execution, situation signals (use a fixed 'normal' state).

## Acceptance criteria
Tick in `phases.json` with evidence when met.
- [x] **ac-1** 'send message to Rahul' parses to Intent(verb=send, object=message, target=Rahul) — unit test passes  
  _Evidence:_ tests/test_intent_resolver.py::test_send_message_to_rahul (+ test_documented_examples, 7 README/grammar cases)
- [x] **ac-2** 'use gmail' resolves to tool id gmail via command_aliases.yaml; 'dry run' / 'preview only' / 'ask before send' / 'auto execute' set the intent's autonomy modifier — unit tests pass  
  _Evidence:_ tests/test_intent_resolver.py::test_use_gmail_directive, ::test_autonomy_modifiers[4 cases], ::test_modifier_and_directive_together
- [x] **ac-3** A command with unclear tool or target yields mode=preview (never execute) — unit test passes  
  _Evidence:_ tests/test_intent_resolver.py::test_unclear_commands_go_to_preview[6 cases], ::test_modifier_after_unknown_tool_does_not_hide_it
- [x] **ac-4** autonomy_guard returns requires_confirmation=True for every never_autonomous category and for high/critical risk at every level — parametrised test passes  
  _Evidence:_ tests/test_autonomy_guard.py::test_never_autonomous_requires_confirmation_at_every_level[24 cases], ::test_high_and_critical_risk_require_confirmation_at_every_level[8 cases]
- [x] **ac-5** Confirmation loop shows plan + tool target and proceeds only on explicit 'yes' — test with scripted input covers yes/no/empty  
  _Evidence:_ tests/test_confirmation_loop.py (12 tests: yes/no/empty/'y'/EOF/Ctrl-C, plan+tool shown first); tests/test_cli.py::test_shell_confirm_yes_and_no
- [x] **ac-6** Interactive CLI loop (prompt-toolkit) reads a command and prints the parsed intent and required autonomy — CliRunner/scripted-input test passes  
  _Evidence:_ tests/test_cli.py::test_shell_prints_intent_and_autonomy (+3 shell tests); prompt-toolkit TTY path checked manually in a pty: prompt, plan, 'Confirmed' all shown

## Depends on
[phase-00-foundation](phase-00-foundation.md)

## OKF concepts touched
- [modules/brain.md](../okf/modules/brain.md)
- [modules/execution.md](../okf/modules/execution.md)
- [modules/interfaces.md](../okf/modules/interfaces.md)
- [apis/command-grammar.md](../okf/apis/command-grammar.md)
- [flows/confirmation-loop.md](../okf/flows/confirmation-loop.md)

## Notes
Done. Out-of-scope follow-ups: situation input is fixed at 'normal' (Phase 6); audit logging of confirmations lands with the router (Phase 4).

plan.md Phase 1 (Week 2). Exit: system parses commands into structured intents.
