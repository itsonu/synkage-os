# Current state — Synkage Core

_Rewritten at the end of every session. This is the cold-start resume point._

- **Project status:** in_progress
- **Active phase:** phase-01-brain — see [phase file](../phases/phase-01-brain.md)
- **Next action:** Create `synkage/brain/intent_resolver.py` with a pydantic `Intent` model and a parser for `<action> <object> [target] [options]` that uses the loaded `CommandAliases`; first test: `send message to Rahul` → verb=send, object=message, target=Rahul (phase-01 ac-1).

## In progress
Nothing mid-flight. Phase 0 is done.

## Blockers
None for Phase 1.

## Open questions / unknowns
Do not guess these — ask the user when the phase that needs them starts.
1. **LLM or not (blocks Phase 3 text skills):** do summarize/draft/classify skills call an LLM (which provider?) or stay rule-based? Spec only says "no heavy model dependency required".
2. **Target OS (Phase 5):** Sticky Notes is Windows-only. Which OS is primary, and what's the note target on Linux/macOS?
3. **Browser sessions (Phase 5):** how WhatsApp Web / Gmail logins persist for Playwright. Involves credentials → needs a human.
4. **Memory location (Phase 7):** spec says repo `memory/`; personal data probably belongs in a user data dir (e.g. `~/.synkage/`).
5. **Trust score (Phases 6–7):** how it's computed and what moves it.
6. **OpenClaw API (Phase 8):** no contract in the spec.
7. **Hotkeys / voice stub:** listed in `docs/proj.md` but not in any phase.

## Recent evidence
- `python -m pytest -q` → 17 passed.
- `python scripts/run_synkage.py` → exit 0, prints system state.
- `ruff check .` / `ruff format --check .` clean.
- `python docs/okf/.tools/okf_lint.py --repo . --bundle docs/okf` → 0 errors.
- `python scripts/phases_status.py` → exit 0, current phase phase-01-brain.
