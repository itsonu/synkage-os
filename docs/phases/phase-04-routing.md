---
type: Phase
title: Execution routing
description: An intent routes through the autonomy router to an adapter and returns a normalised result.
timestamp: 2026-09-24T18:48:00Z
tags: [phase]
---

## Status
done

## Goal
An intent routes through the autonomy router to an adapter and returns a normalised result.

## Scope
**In:** adapters/tool_adapter_base.py, local_exec_adapter, openclaw_adapter stub, execution/autonomy_router.py, action_planner.py, audit log.
**Out:** Real browser/desktop control, real OpenClaw calls.

## Acceptance criteria
Tick in `phases.json` with evidence when met.
- [x] **ac-1** tool_adapter_base defines execute() → ExecutionResult; local_exec and openclaw stub implement it — tests pass  
  _Evidence:_ tests/test_adapters.py (12 tests): test_adapters_implement_contract[LocalExecAdapter, OpenClawAdapter], test_tool_adapter_is_abstract, local_exec controller dispatch/crash/unavailable, openclaw stub, builder drafts validate as ActionRequest
- [x] **ac-2** Router picks the adapter named by the tool's registry entry — test passes  
  _Evidence:_ tests/test_router.py::test_router_uses_registry_adapter, ::test_registry_beats_adapter_named_in_draft, ::test_unknown_adapter_fails, ::test_disabled_tool_is_unavailable_and_adapter_not_called
- [x] **ac-3** Router refuses to execute an unconfirmed high/critical or never_autonomous action — test passes  
  _Evidence:_ tests/test_router.py::test_unconfirmed_high_or_critical_is_refused[4 cases], ::test_never_autonomous_refused_even_with_tampered_decision, ::test_default_level_2_needs_confirmation, ::test_level_below_2_is_refused, ::test_not_ready_draft_is_refused
- [x] **ac-4** Every execution appends an audit record with intent, tool, autonomy level, confirmation state, result — test reads it back  
  _Evidence:_ tests/test_router.py::test_every_routed_action_is_audited (reads back success/refused/dry_run records: intent, tool, adapter, level, risk, confirmation, result), ::test_audit_records_router_derived_categories, ::test_audit_is_append_only_jsonl, ::test_adapter_exception_is_failed_and_audited
- [x] **ac-5** 'dry run' produces a plan and result without calling the adapter — test passes  
  _Evidence:_ tests/test_router.py::test_dry_run_never_calls_adapter, ::test_dry_run_reports_unavailable_tool; tests/test_cli.py::test_run_dry_run_executes_nothing

## Depends on
[phase-03-skills](phase-03-skills.md)

## OKF concepts touched
- [modules/execution.md](../okf/modules/execution.md)
- [modules/adapters.md](../okf/modules/adapters.md)
- [data-models/tool-registry.md](../okf/data-models/tool-registry.md)

## Notes
Done. Audit log is `logs.jsonl` (gitignored, `SYNKAGE_AUDIT_LOG` overrides). All seeded tools are `enabled: false` and `local_exec` has no controllers, so real commands end `unavailable` until Phase 5. `rollback.py` not built (not in this phase's criteria). Added in passing: a safer modifier at the end of message text forces preview.

plan.md Phase 4 (Week 5). Audit fields from docs/autonomy_safety.md.
