---
type: Module
title: Logging setup
description: Configures the synkage logger with a rich handler on stderr.
timestamp: 2026-09-24T18:48:53Z
sources:
  - synkage/logging_setup.py
---

## Status
built (Phase 0)

## Interface
`setup_logging(level=None)` — level from arg > `SYNKAGE_LOG_LEVEL` > `INFO`. Logs to **stderr** so stdout stays clean for command output. Called by the [CLI](cli.md).

## Not covered
The execution audit log (intent, tool, level, confirmation, result) is separate — planned in [execution](execution.md).
