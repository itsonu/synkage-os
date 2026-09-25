---
type: Phase
title: Situation awareness
description: Autonomy thresholds change with detected situation state.
timestamp: 2026-09-24T18:48:00Z
tags: [phase]
---

## Status
done

## Goal
Autonomy thresholds change with detected situation state.

## Scope
**In:** activity_monitor, time_context, situation_detector (Idle/Normal/Focused/Urgent/Emergency), urgency rules, threshold adjustment.
**Out:** Vision, continuous listening, model-based detection.

## Acceptance criteria
Tick in `phases.json` with evidence when met.
- [x] **ac-1** situation_detector maps fixture signal sets to each of the 5 states — parametrised test passes  
  _Evidence:_ tests/test_situation.py::test_fixture_signals_map_to_each_state[idle, normal, focused, urgent, emergency] (+ ::test_rule_priority, 8 cases)
- [x] **ac-2** Same intent gets a different confirmation requirement in Focused vs Idle — test passes  
  _Evidence:_ tests/test_situation_autonomy.py::test_same_intent_focused_vs_idle ('save note meeting at 4pm': focused -> no confirmation, idle -> confirmation), ::test_focused_vs_idle_through_prime, ::test_focused_vs_idle_through_router; tests/test_cli.py::test_focused_skips_confirmation_for_low_risk_but_idle_asks
- [x] **ac-3** Never-autonomous and high/critical still require confirmation in every state — test passes  
  _Evidence:_ tests/test_situation_autonomy.py::test_never_autonomous_confirms_in_every_state[30 cases], ::test_high_and_critical_confirm_in_every_state[10 cases], ::test_router_refuses_flagged_low_risk_even_when_situation_allows_auto[3], ::test_config_rejects_auto_for_high_or_critical[2]
- [x] **ac-4** CLI status shows the current situation state  
  _Evidence:_ python scripts/run_synkage.py status -> 'Situation: normal (no rule matched)'; tests/test_cli.py::test_status_shows_situation, ::test_status_with_forced_situation_shows_effect

## Depends on
[phase-04-routing](phase-04-routing.md)

## OKF concepts touched
- [modules/context.md](../okf/modules/context.md)
- [modules/brain.md](../okf/modules/brain.md)

## Notes
Done while Phase 5 waits on the user's manual checks (Phase 6 depends only on Phase 4). Policy per state is inferred (ADR-0009): focused/urgent/emergency let low-risk actions skip confirmation. Urgency words count only before ':'. Not built: execution-speed / interruption policy, `app_context.py`, watchdog file signals.

plan.md Phase 6 (Week 7). Rule-based per ADR-0003.
