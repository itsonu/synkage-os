---
type: Flow
title: Night cycle
description: Scheduled job that compresses logs and adjusts trust.
timestamp: 2026-09-24T18:48:53Z
---

## Status
planned — [Phase 7](../../phases/phase-07-memory.md). Scheduler: apscheduler; entry `scripts/nightly_update.py`.

## Steps
Log compression → pattern promotion → trust adjustment → behavior decay. Reads/writes the [memory store](../data-models/memory-store.md).
