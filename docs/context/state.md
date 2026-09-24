# Current state — Synkage Core

_Rewritten at the end of every session. This is the cold-start resume point._

- **Project status:** in_progress
- **Active phase:** phase-05-tool-control — see [phase file](../phases/phase-05-tool-control.md)
- **Next action:** Build a Playwright browser controller in `synkage/tools/browser/` and test it against a **local** HTML page (phase-05 ac-1; no network, no accounts). Then build the WhatsApp Web / Gmail draft flows against **mock pages** (ac-2, ac-3 automated parts). Register controllers in `synkage/adapters/local_exec_adapter.CONTROLLERS`.

## In progress
Nothing mid-flight. Phases 0–4 are done.

## Blockers
Phase 5 is the first phase that touches real accounts. These parts **need the user**; per the CLAUDE.md guardrails, never do them unattended:
- **Manual runs** for ac-2/ac-3 need a logged-in WhatsApp Web / Gmail session on the user's machine. Logging in is credential handling, and sending is acting as the user.
- **Sticky Notes (ac-4)** is Windows-only; this dev container is Linux. Needs the target-OS answer (open question 2).
- **Enabling tools (ac-5)** in `tool_registry.json` makes real actions possible. Flip them only once the controllers are tested.
The automated parts (ac-1, mock-page tests for ac-2/ac-3) are unblocked.

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
- `python -m pytest -q` → 217 passed.
- `python scripts/run_synkage.py run "send message to Raj dry run: hi"` → `Execution: dry_run — dry run: would route to local_exec, but tool 'whatsapp_web' is disabled in tool_registry.json`, plus an audit record.
- shell: `yes` → `unavailable` (tool disabled); `no` → `refused`; both audited to `logs.jsonl`.
- ruff clean; OKF lint 0 errors; `phases_status.py` → current phase phase-05-tool-control.
