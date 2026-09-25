# Session log — Synkage Core

Append-only, newest first. One entry per working session: what changed, what was decided, what's next.

---

## 2026-09-25 — Phase 7 (Memory & night cycle) done
- User chose the suggested defaults: memory in `~/.synkage/memory`; trust moved by outcomes with decay.
- `synkage/memory/store.py` (0700 dir, profile + relationship state, atomic writes, created on first CLI run), `night_cycle.py` (decay per elapsed day then outcome deltas; lossless compression into daily summaries + gzip archive; exclusive flock), `scripts/nightly_update.py` (once / `--schedule` via apscheduler 3.11).
- New `config/memory.yaml` + `MemoryConfig`. The audit log's default moved to `<memory dir>/logs.jsonl`, and `AuditLog.append` now takes the flock.
- CLI `status` shows the memory dir, trust and last cycle.
- Verified: a race test fails 5/5 without the lock. The JSON-output CLI test now reads stdout (the first-run log goes to stderr).
- Not built: pattern promotion; trust → autonomy wiring (deliberately; ADR-0010).
- Tests: 376 passed + 1 skipped. Blocked next: Phase 5 (user), Phase 8 (OpenClaw API), Phase 9 (locked).

## 2026-09-25 — Phase 6 (Situation awareness) done
- Context layer: `time_context` (quiet hours, midnight wrap), `activity_monitor` (macOS `ioreg` idle time + frontmost app via osascript; failures → unknown), `signal_ingestion` (snapshot + urgent/emergency words).
- Brain: `situation_detector` (7 ordered rules, unknown never triggers); `Prime.situation()`, `PrimeResult.situation`; the guard applies `states.<state>.auto_risk` at level 2, before the hard rules.
- Config: new `config/situation.yaml` + `SituationConfig` (five states required; auto for high/critical rejected).
- CLI: global `--situation`; `status` shows the situation and what it relaxes; `parse`/`run` show a Situation line. The audit log records the situation.
- Decisions (inferred, ADR-0009): focused/urgent/emergency → low-risk runs without confirmation; idle/normal unchanged.
- Found in self-review: urgency words in message text were loosening confirmation (inconsistent with the Phase 4 rule) → now only the command before ':' counts. Tests on a Mac would have read real probes (Terminal → focused) → autouse fixture pins neutral signals.
- Tests: 346 passed + 1 skipped. Phase 5 still waits on the user's manual checks.

## 2026-09-24 — Phase 5 (Tool control), automated part
- User answers: primary OS **macOS**; do only the parts that don't touch their accounts.
- Tools layer: `BrowserSession` (persistent profile outside the repo, lazy launch), `WhatsAppWeb` (phone link or exact-name search; `send` only the exact drafted text; duplicate names refused), `Gmail` (drafts only, never sends), `AppleNotes` (osascript with argv, no injection).
- Adapters: `local_exec` `HANDLERS` translate requests into controller calls; new optional `supports_draft/draft/discard`; `ExecutionStatus.drafted`.
- Router: `draft()` before confirmation (not for flagged or high/critical actions); `route(..., drafted=True)` clears the draft on `no`. CLI: draft → confirm → route; new `login` command.
- Config: new `apple_notes` tool; notes preference → apple_notes; `apple notes` directive. All tools still disabled.
- Tests: mock WhatsApp/Gmail pages on a local HTTP server with headless Chromium; an autouse guard makes the real shared browser raise in tests; CI installs Chromium. The container needs `SYNKAGE_CHROMIUM_PATH`-style fallback (Playwright 1.63 expects a newer build than the one installed).
- Found in review: a test helper waited 30 s on a blank page (the app was correct); duplicate contact names could pick the wrong recipient (now refused).
- Tests: 251 passed + 1 skipped. Next: the user's manual checks (runbook), then ac-5.

## 2026-09-24 — Phase 4 (Routing) done
- Adapters: `ActionRequest` (= builder draft, `extra="forbid"`), `ExecutionResult`/`ExecutionStatus`, `ToolAdapter`; `local_exec` (CONTROLLERS dict, empty → `unavailable`), `openclaw` stub; `adapters/registry.ADAPTERS`.
- Execution: `action_planner` (adapter from the registry, **re-derives** risk and categories), `autonomy_router.route` (blocked → dry run → level → confirmation → skipped/unavailable → adapter; audits every outcome), `audit.py` (`logs.jsonl`, `SYNKAGE_AUDIT_LOG`).
- CLI: new `run "<cmd>"`; `shell` now routes. Both share `_process`.
- Found while testing: `…: hi dry run` silently ran as a normal send, because content options are ignored. Fix: a safer modifier at the end of content → preview with a hint; `auto execute` in content is still ignored. A level-2 dry run now reports "needs confirmation" for the real run.
- Self-inflicted during testing: a skipped ruff step left env vars unset, so one `run` wrote to the repo's `runs/` and `logs.jsonl` (both gitignored, deleted). A first piped shell run hung and couldn't be reproduced afterwards (the crash path exits cleanly).
- Decision (user didn't choose): audit log = `logs.jsonl` at the repo root, as recommended.
- Tests: 217 passing. Next: Phase 5; its real-account parts need the user.

## 2026-09-24 — Phase 3 (Skills) done
- Built `synkage/skills/base_skill.py` and `registry.py` (duplicate rejection, permission check **before** input validation, fresh instance per call, output type check, `for_agent()` client).
- Skills (rule-based): `decision/plan_steps` (the planner's templates moved here), `analysis/classify_intent`, `text/format_note`.
- Permissions: `agent_skills` in `config/permissions.yaml`, default deny (planner: plan_steps + classify_intent; builder: format_note; reporter: none).
- Agents take `(config, skills)`; Prime shares one registry. Builder adds a formatted `note` to ready note drafts. New `skills` CLI command.
- Boundary test: agents may import only `synkage.skills.registry`.
- Decision (user didn't answer the LLM question): shipped 3 of 5 skills; summarize + draft_message deferred.
- Noticed: "buy" is a payments keyword, so `save note buy milk` needs confirmation. By design (conservative), but it may annoy in practice.
- Tests: 174 passing. Next: Phase 4 (routing).

## 2026-09-24 — Phase 2 (Agents) done
- Built the agent contract (`synkage/agents/base_agent.py`: `AgentTask`, `AgentResult`, `Artifact`, `BaseAgent.run`), plus planner, builder and reporter agents and `registry.AGENTS`.
- `Prime.delegate` + `select_chain`: level 0 → no agents; preview / level 1 / unknown verb / `plan` → planner → reporter; otherwise planner → builder → reporter. It stops at the first failure.
- Artifacts are JSON files in `runs/<run-id>/NN-<agent>.json` (gitignored; `SYNKAGE_RUNS_DIR` overrides). Agents read earlier work only from those files.
- CLI: new `prepare "<cmd>"`; `shell` now prepares and shows the report **before** asking for confirmation.
- New invariant test `tests/test_layer_boundaries.py` (agents/brain/skills/avatar import rules).
- Decision (user didn't choose): runs dir = gitignored `runs/`. Tests use a temp dir via an autouse fixture.
- Tests: 140 passing. Next: Phase 3 (skills). The LLM question blocks only the summarize/draft skills.

## 2026-09-24 — Phase 1 (Brain) done
- Built `synkage/brain/intent_resolver.py` (rule-based parser → `Intent`), `autonomy_guard.py` (→ `AutonomyDecision`), `prime.py` (`Prime.handle`), `synkage/execution/confirmation_loop.py` (only `yes` confirms).
- CLI: `parse "<cmd>" [--json]` and interactive `shell` (prompt-toolkit on a TTY, `input()` otherwise). Nothing executes yet.
- Config: `command_aliases.yaml` verbs are now `{needs_target, needs_tool}` rules plus `object_types`; `permissions.yaml` gained `category_keywords` (every category needs ≥1).
- Decisions: tool resolution order directive > inline mention > preference; hard-rule `requires_confirmation` stays true at every level even when nothing runs; options are parsed before `use <tool>` so a modifier can't hide an unknown tool (found in self-review, regression-tested).
- Known limitation: `use` anywhere in the head is read as a tool directive (`summarize how to use docker` → preview).
- Tests: 106 passing. Next: Phase 2 — agent task contract.

## 2026-09-24 — Genesis + Phase 0 (Foundation)
- Workspace: CLAUDE.md operating contract, OKF bundle in `docs/okf/` (tools vendored in `.tools/`), phase tracker in `docs/phases/` (numbering follows `docs/plan.md`, Phases 0–9), context layer.
- Code: `synkage/` package with 10 layer subpackages; `synkage/config.py` (pydantic-validated loader for 5 config files, cross-file checks, non-removable hard safety rules); `synkage/logging_setup.py`; Typer CLI (`scripts/run_synkage.py`, `python -m synkage`) printing system state.
- Config seeded from docs: autonomy_levels, permissions, command_aliases, app_preferences, tool_registry.json (+ generated JSON Schema).
- Tests: 17 passing. CI: `.github/workflows/ci.yml` (ruff, pytest, CLI boot, OKF lint, phase board).
- Decisions: ADR-0001…0007. Notable: code in `synkage/` not flat top-level dirs; `tool_registry.json` in `config/` (ADR-0006); config may tighten but not loosen safety rules (ADR-0002).
- Next: Phase 1 — intent resolver (see state.md).
