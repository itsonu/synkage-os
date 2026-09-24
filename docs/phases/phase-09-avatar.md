---
type: Phase
title: Avatar layer (locked)
description: Avatar reflects system state without controlling logic.
timestamp: 2026-09-24T18:48:00Z
tags: [phase]
---

## Status
todo

## Goal
Avatar reflects system state without controlling logic.

## Scope
**In:** Unity avatar, emotion_axes, state_mapper, websocket bridge.
**Out:** Any decision or execution from the avatar.

## Acceptance criteria
Tick in `phases.json` with evidence when met.
- [ ] **ac-1** state_mapper emits avatar state for each system state — test passes
- [ ] **ac-2** Websocket bridge streams state to a client — integration test passes
- [ ] **ac-3** Avatar has no code path into brain/execution — import-boundary test passes

## Depends on
[phase-05-tool-control](phase-05-tool-control.md), [phase-06-situation](phase-06-situation.md), [phase-07-memory](phase-07-memory.md)

## OKF concepts touched
- [modules/avatar.md](../okf/modules/avatar.md)

## Notes
Locked until MVP is stable, execution reliable, and the autonomy guard tested (plan.md).
