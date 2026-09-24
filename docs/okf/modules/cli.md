---
type: Module
title: CLI
description: Typer app that loads config and prints system state.
timestamp: 2026-09-24T18:58:38Z
sources:
  - synkage/interfaces/cli.py
  - synkage/__main__.py
  - scripts/run_synkage.py
---

## Status
built (Phase 0; `parse` and `shell` added in Phase 1)

## Interface
| Invocation | Effect |
|---|---|
| `python scripts/run_synkage.py` | Load config, print system state (same as `status`) |
| `… status` | Print autonomy default, risk classes, never-autonomous list, tools table |
| `… parse "<command>" [--json]` | Show parsed intent + autonomy decision. Executes nothing |
| `… shell` | Interactive loop: parse each line, run the [confirmation loop](../flows/confirmation-loop.md) when required. Executes nothing until Phase 4. `exit`/`quit`/EOF leaves |
| `… version` | Print version |
| `--config-dir DIR` | Use another config directory |
| `--log-level LEVEL` | DEBUG / INFO / WARNING / ERROR |

`python -m synkage` is equivalent. Exit code **1** on any [config error](config-loader.md).

## Behaviour
The Typer callback runs for every command: sets up [logging](logging.md), calls `load_config`, stores the result on `ctx.obj`. Only rendering lives here — part of the [interface layer](interfaces.md). `parse`/`shell` call [Prime](brain.md). See [startup flow](../flows/startup.md).

## Gotchas
- `shell` uses prompt-toolkit only when stdin is a TTY; otherwise plain `input()` (this is what tests drive).
- User text is escaped before rich renders it, so `[red]` in a command prints literally.
`scripts/run_synkage.py` inserts the repo root into `sys.path` because the package isn't pip-installed.
