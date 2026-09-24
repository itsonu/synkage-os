---
type: Phase
title: Foundation
description: Repo structure, config system, logging, and a bootable CLI that prints system state.
timestamp: 2026-09-24T18:48:00Z
tags: [phase]
---

## Status
done

## Goal
Repo structure, config system, logging, and a bootable CLI that prints system state.

## Scope
**In:** Layer package skeleton, config loader + validation, seed config files, tool_registry.json schema, logging, CLI entry, tests, CI, genesis workspace (CLAUDE.md, OKF, phases, context).
**Out:** Any intent parsing, agents, skills, adapters, or real tool control.

## Acceptance criteria
Tick in `phases.json` with evidence when met.
- [x] **ac-1** synkage/<layer>/__init__.py exists for all 10 layers  
  _Evidence:_ files synkage/{brain,agents,skills,execution,adapters,tools,context,memory,avatar,interfaces}/__init__.py
- [x] **ac-2** pip install -r requirements.txt succeeds on Python 3.10+  
  _Evidence:_ pip install -r requirements.txt ruff → exit 0 (Python 3.11.15)
- [x] **ac-3** load_config validates all five config files; invalid config raises ConfigError naming the file  
  _Evidence:_ tests/test_config.py — 13 tests pass (python -m pytest -q → 17 passed)
- [x] **ac-4** python scripts/run_synkage.py exits 0 and prints autonomy default, risk classes, never-autonomous list, tools  
  _Evidence:_ tests/test_cli.py::test_entry_script_boots, ::test_no_args_prints_status
- [x] **ac-5** Bad --config-dir exits 1 with an error on stderr  
  _Evidence:_ tests/test_cli.py::test_bad_config_dir_exits_1
- [x] **ac-6** Logging level honours --log-level and SYNKAGE_LOG_LEVEL  
  _Evidence:_ run_synkage.py --log-level DEBUG version → 'DEBUG Loaded config from …/config' on stderr; same with SYNKAGE_LOG_LEVEL=DEBUG
- [x] **ac-7** config/schema/tool_registry.schema.json is committed and matches the pydantic model  
  _Evidence:_ tests/test_config.py::test_committed_schema_matches_model
- [x] **ac-8** ruff check, ruff format --check, OKF lint (0 errors) and phases_status.py all pass  
  _Evidence:_ ruff: All checks passed; okf_lint: 0 errors; phases_status: exit 0

## Depends on
none

## OKF concepts touched
- [modules/cli.md](../okf/modules/cli.md)
- [modules/config-loader.md](../okf/modules/config-loader.md)
- [modules/logging.md](../okf/modules/logging.md)
- [data-models/tool-registry.md](../okf/data-models/tool-registry.md)
- [data-models/autonomy-policy.md](../okf/data-models/autonomy-policy.md)
- [data-models/command-vocabulary.md](../okf/data-models/command-vocabulary.md)
- [data-models/app-preferences.md](../okf/data-models/app-preferences.md)
- [flows/startup.md](../okf/flows/startup.md)

## Notes
plan.md Phase 0 (Week 1). Exit criterion from plan.md: CLI starts, loads config, prints system state.
