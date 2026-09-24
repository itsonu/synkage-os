---
type: Phase
title: Memory & night cycle
description: State persists across runs and a nightly job updates trust.
timestamp: 2026-09-24T18:48:00Z
tags: [phase]
---

## Status
todo

## Goal
State persists across runs and a nightly job updates trust.

## Scope
**In:** user_profile.json, relationship_state.json, logs.json, night_cycle.py, scripts/nightly_update.py, log compression, behavior decay.
**Out:** Cloud sync, multi-device.

## Acceptance criteria
Tick in `phases.json` with evidence when met.
- [ ] **ac-1** Memory files are created on first run at the chosen location and survive restart — test passes
- [ ] **ac-2** night_cycle compresses logs older than N days into a summary — test passes
- [ ] **ac-3** night_cycle changes the trust score from logged outcomes — test passes
- [ ] **ac-4** scripts/nightly_update.py runs the cycle once and exits 0; apscheduler job registered — test passes

## Depends on
[phase-04-routing](phase-04-routing.md)

## OKF concepts touched
- [modules/memory.md](../okf/modules/memory.md)
- [data-models/memory-store.md](../okf/data-models/memory-store.md)
- [flows/night-cycle.md](../okf/flows/night-cycle.md)

## Notes
plan.md Phase 7 (Week 8). Decide memory location first (state.md Unknowns).
