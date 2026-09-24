---
type: Phase
title: Situation awareness
description: Autonomy thresholds change with detected situation state.
timestamp: 2026-09-24T18:48:00Z
tags: [phase]
---

## Status
todo

## Goal
Autonomy thresholds change with detected situation state.

## Scope
**In:** activity_monitor, time_context, situation_detector (Idle/Normal/Focused/Urgent/Emergency), urgency rules, threshold adjustment.
**Out:** Vision, continuous listening, model-based detection.

## Acceptance criteria
Tick in `phases.json` with evidence when met.
- [ ] **ac-1** situation_detector maps fixture signal sets to each of the 5 states — parametrised test passes
- [ ] **ac-2** Same intent gets a different confirmation requirement in Focused vs Idle — test passes
- [ ] **ac-3** Never-autonomous and high/critical still require confirmation in every state — test passes
- [ ] **ac-4** CLI status shows the current situation state

## Depends on
[phase-04-routing](phase-04-routing.md)

## OKF concepts touched
- [modules/context.md](../okf/modules/context.md)
- [modules/brain.md](../okf/modules/brain.md)

## Notes
plan.md Phase 6 (Week 7). Rule-based per ADR-0003.
