---
type: Flow
title: Execution routing
description: How a prepared action draft is gated, routed to an adapter, and audited.
timestamp: 2026-09-25T13:31:09Z
sources:
  - synkage/execution/autonomy_router.py
  - synkage/execution/action_planner.py
---

## Status
built (Phase 4)

## Draft step (`AutonomyRouter.draft`, Phase 5)
Before confirmation, the router may stage the action (fill the WhatsApp message) so the user sees it. It only does this in execute mode with `may_execute`, a ready, enabled, known tool, **no never-autonomous categories and no high/critical risk**, and an adapter that `supports_draft`. The outcome (`drafted` / `failed`) is audited. If the draft fails, the CLI stops before asking. `route(..., drafted=True)` clears the draft when the answer is `no` ("(draft cleared)"). See [ADR-0008](../decisions/0008-macos-tool-control.md).

## Steps (`AutonomyRouter.route`)
1. **Plan** ([execution](../modules/execution.md) action planner):
   - The adapter is taken from the tool's [registry](../data-models/tool-registry.md) entry, not from the draft; a mismatch is noted in `reasons`.
   - Risk comes from the registry. Categories are the decision's plus a fresh keyword match on the raw command.
   - For a level-2 dry run, `requires_confirmation=True`, so the dry run reports what a real run needs.
2. **Blocked** (draft not ready, or unknown tool) → `refused`.
3. **Dry run** → `dry_run`, with steps and whether a real run would need confirmation. **The adapter is never called.**
4. `may_execute` is false (level < 2, preview) → `refused`.
5. Confirmation required but missing or not `yes` → `refused`. This covers never-autonomous categories and high/critical risk **even if the decision was tampered with**.
6. No tool (e.g. `summarize`) → `skipped`. Tool `enabled: false` → `unavailable`.
7. Unknown adapter name → `failed`. Otherwise `adapter.execute(request)`; an adapter exception → `failed`.
8. **Audit every outcome**, refusals and dry runs included ([audit log](../data-models/audit-log.md)), with the `situation` that shaped the decision (e.g. a focused low-risk action that ran without confirmation).

## Driven by
The [CLI](../modules/cli.md) runs parse → [agent chain](agent-chain.md) → [confirmation loop](confirmation-loop.md) (only when execute mode, `may_execute`, draft ready, and the plan requires it) → route. Preview and plan-only chains produce no draft, so nothing is routed or audited.
