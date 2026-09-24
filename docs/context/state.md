# Current state — Synkage Core

_Rewritten at the end of every session. This is the cold-start resume point._

- **Project status:** in_progress
- **Active phase:** phase-02-agents — see [phase file](../phases/phase-02-agents.md)
- **Next action:** Create `synkage/agents/base_agent.py` with a pydantic task contract (`AgentTask`: intent, input artifacts, output artifact path; `AgentResult`: status, artifact path) and an abstract `BaseAgent.run(task)`; first test checks the contract validates and a trivial subclass writes its artifact (phase-02 ac-1). Decide the artifact directory first (suggest a per-task folder under a gitignored `runs/`).

## In progress
Nothing mid-flight. Phases 0–1 are done.

## Blockers
None for Phase 2.

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
- `python -m pytest -q` → 106 passed.
- `python scripts/run_synkage.py parse "send message to Rahul"` → verb send / object message / target Rahul, level 2, confirmation required.
- `python scripts/run_synkage.py shell` → confirmation loop accepts only `yes` (tested via CliRunner and a real pty).
- `ruff check .` / `ruff format --check .` clean; OKF lint 0 errors; `phases_status.py` → current phase phase-02-agents.
