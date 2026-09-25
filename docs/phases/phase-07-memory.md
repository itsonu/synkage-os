---
type: Phase
title: Memory & night cycle
description: State persists across runs and a nightly job updates trust.
timestamp: 2026-09-24T18:48:00Z
tags: [phase]
---

## Status
done

## Goal
State persists across runs and a nightly job updates trust.

## Scope
**In:** user_profile.json, relationship_state.json, logs.json, night_cycle.py, scripts/nightly_update.py, log compression, behavior decay.
**Out:** Cloud sync, multi-device.

## Acceptance criteria
Tick in `phases.json` with evidence when met.
- [x] **ac-1** Memory files are created on first run at the chosen location and survive restart — test passes  
  _Evidence:_ tests/test_memory_store.py (6 tests): ::test_first_run_creates_dir_and_files (0700), ::test_second_run_creates_nothing_and_never_overwrites, ::test_state_survives_restart, ::test_cli_first_run_creates_memory, ::test_default_location_is_outside_the_repo
- [x] **ac-2** night_cycle compresses logs older than N days into a summary — test passes  
  _Evidence:_ tests/test_night_cycle.py::test_old_records_become_daily_summaries_and_are_archived (lossless: summaries + gzip archive), ::test_summaries_merge_across_runs, ::test_second_run_compresses_nothing_more, ::test_no_record_lost_when_appends_race_the_cycle (fails 5/5 with the lock disabled)
- [x] **ac-3** night_cycle changes the trust score from logged outcomes — test passes  
  _Evidence:_ tests/test_night_cycle.py::test_trust_moves_with_logged_outcomes, ::test_outcome_mapping[7], ::test_outcomes_are_counted_once, ::test_trust_decays_toward_neutral_per_day_elapsed[3], ::test_trust_is_clamped
- [x] **ac-4** scripts/nightly_update.py runs the cycle once and exits 0; apscheduler job registered — test passes  
  _Evidence:_ tests/test_night_cycle.py::test_nightly_script_runs_once_and_exits_0, ::test_scheduler_registers_daily_job (job 'night_cycle', cron 03:17), ::test_nightly_script_bad_config_exits_1

## Depends on
[phase-04-routing](phase-04-routing.md)

## OKF concepts touched
- [modules/memory.md](../okf/modules/memory.md)
- [data-models/memory-store.md](../okf/data-models/memory-store.md)
- [flows/night-cycle.md](../okf/flows/night-cycle.md)

## Notes
Done (user chose the suggested defaults, ADR-0010): memory in `~/.synkage/memory` (0700), audit log moved there, trust from confirmed/declined/failed outcomes with daily decay, lossless compression. Trust is stored and shown but not yet wired into autonomy. Not built: pattern promotion.

plan.md Phase 7 (Week 8). Decide memory location first (state.md Unknowns).
