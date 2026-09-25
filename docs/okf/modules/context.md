---
type: Module
title: Signal and context layer
description: Collects activity, app, time and command-keyword signals for situation detection.
timestamp: 2026-09-25T13:30:46Z
sources:
  - synkage/context/__init__.py
  - synkage/context/time_context.py
  - synkage/context/activity_monitor.py
  - synkage/context/signal_ingestion.py
---

## Status
built (Phase 6). `app_context.py` is not built (the frontmost app lives in the activity monitor). No watchdog file signals yet.

## Files
| File | Signal |
|---|---|
| `time_context.py` | `time_signals(quiet_hours, now) -> TimeSignals(now, quiet_hours)`; `in_window()` handles windows that wrap midnight |
| `activity_monitor.py` | `ActivityMonitor(runner, platform).read() -> ActivitySignals(idle_seconds, frontmost_app)`. macOS only: `ioreg -c IOHIDSystem` (HIDIdleTime) and osascript/System Events (asks for Automation permission once). Any failure → `None` (unknown), never a guess |
| `signal_ingestion.py` | `SignalCollector.collect(command, override, now) -> Signals`: time + activity + urgent/emergency words (**command before `:` only**) + override |

## Rules
Context reports; it decides nothing. It doesn't import brain, agents, skills, execution or adapters (`tests/test_layer_boundaries.py`). Tests pin signals with an autouse fixture (no real probes, midday), so results don't depend on the machine running them.

## Connections
Read by the [situation detector](situation-detector.md). Configured by the [situation config](../data-models/situation-config.md).
