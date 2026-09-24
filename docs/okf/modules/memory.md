---
type: Module
title: Memory layer
description: File-based project and user state plus the night learning cycle.
timestamp: 2026-09-24T18:48:53Z
sources:
  - synkage/memory/__init__.py
---

## Status
scaffolded — planned for [Phase 7](../../phases/phase-07-memory.md).

## Responsibilities
Persist user profile, relationship state, interaction logs; run the [night cycle](../flows/night-cycle.md). See [memory store](../data-models/memory-store.md) and [ADR-0004](../decisions/0004-local-file-memory.md).

## Planned files
`night_cycle.py` (code) plus data files — location undecided (see memory store Unknowns).
