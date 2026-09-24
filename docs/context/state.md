# Current state — Synkage Core

_Rewritten at the end of every session. This is the cold-start resume point._

- **Project status:** in_progress
- **Active phase:** phase-04-routing — see [phase file](../phases/phase-04-routing.md)
- **Next action:** Create `synkage/adapters/tool_adapter_base.py` with an `ExecutionResult` model and an abstract `ToolAdapter.execute(draft) -> ExecutionResult`, where `draft` is the builder's `action_draft` body. Then add a `local_exec` adapter that simulates (no real tool calls until Phase 5) and an `openclaw` stub that refuses. First test: both implement the contract (phase-04 ac-1).

## In progress
Nothing mid-flight. Phases 0–3 are done.

## Blockers
None for Phase 4. Decide where the audit log lives (ac-4) before writing it. The simplest option consistent with the spec is an append-only `logs.jsonl` next to `runs/`; the spec's `memory/logs.json` is the Phase 7 home.

## Open questions / unknowns
Do not guess these — ask the user when the phase that needs them starts.
1. **LLM or not (blocks the deferred summarize + draft_message skills):** should they call an LLM (which provider?) or stay rule-based? Spec only says "no heavy model dependency required". Phase 3 shipped without them.
2. **Target OS (Phase 5):** Sticky Notes is Windows-only. Which OS is primary, and what's the note target on Linux/macOS?
3. **Browser sessions (Phase 5):** how WhatsApp Web / Gmail logins persist for Playwright. Involves credentials → needs a human.
4. **Memory location (Phase 7):** spec says repo `memory/`; personal data probably belongs in a user data dir (e.g. `~/.synkage/`). Same question for agent artifacts in `runs/`: they hold message text and are never cleaned up.
5. **Trust score (Phases 6–7):** how it's computed and what moves it.
6. **OpenClaw API (Phase 8):** no contract in the spec.
7. **Hotkeys / voice stub:** listed in `docs/proj.md` but not in any phase.

## Recent evidence
- `python -m pytest -q` → 174 passed.
- `python scripts/run_synkage.py skills` → plan_steps and classify_intent (planner), format_note (builder).
- `prepare "save note buy milk; call mom"` → the builder draft carries note markdown `# Note (2 items)` with bullets.
- ruff clean; OKF lint 0 errors; `phases_status.py` → current phase phase-04-routing.
