---
type: Flow
title: Startup
description: What happens when the CLI boots.
timestamp: 2026-09-24T18:48:53Z
---

## Status
built (Phase 0)

## Steps
1. `scripts/run_synkage.py` (or `python -m synkage`) → [CLI](../modules/cli.md) Typer callback.
2. [Logging setup](../modules/logging.md) with `--log-level` / `SYNKAGE_LOG_LEVEL`.
3. [Config loader](../modules/config-loader.md) resolves the config dir and validates all five files plus cross-file references.
4. On `ConfigError`: log the error, exit 1.
5. No subcommand or `status`: render system state.
