---
type: Phase
title: OpenClaw integration (optional)
description: Synkage delegates execution to OpenClaw safely.
timestamp: 2026-09-24T18:48:00Z
tags: [phase]
---

## Status
deferred — by the user (2026-09-25). Optional phase, and the spec gives no OpenClaw API contract. Resume by setting the status back to `todo` once the API is known.

## Goal
Synkage delegates execution to OpenClaw safely.

## Scope
**In:** openclaw_adapter.py, adapter contract, routing rules, safety boundary.
**Out:** Letting OpenClaw decide autonomy.

## Acceptance criteria
Tick in `phases.json` with evidence when met.
- [ ] **ac-1** openclaw_adapter implements tool_adapter_base against the real OpenClaw API — integration test passes
- [ ] **ac-2** An OpenClaw action mapped to high risk still triggers confirmation — test passes
- [ ] **ac-3** OpenClaw results pass through the brain verifier — test passes

## Depends on
[phase-04-routing](phase-04-routing.md)

## OKF concepts touched
- [services/openclaw-runtime.md](../okf/services/openclaw-runtime.md)
- [modules/adapters.md](../okf/modules/adapters.md)

## Notes
Optional. Needs OpenClaw API details (state.md Unknowns).
