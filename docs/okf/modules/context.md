---
type: Module
title: Signal and context layer
description: Collects activity, app, and time signals for situation detection.
timestamp: 2026-09-24T18:48:53Z
sources:
  - synkage/context/__init__.py
---

## Status
scaffolded — planned for [Phase 6](../../phases/phase-06-situation.md).

## Responsibilities
Emit structured signals to the [brain](brain.md). Decides nothing. File watching via watchdog.

## Planned files
`signal_ingestion.py`, `activity_monitor.py`, `time_context.py`, `app_context.py`.
