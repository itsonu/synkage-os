# Current state — Synkage Core

_Rewritten at the end of every session. This is the cold-start resume point._

- **Project status:** in_progress
- **Active phase:** phase-03-skills — see [phase file](../phases/phase-03-skills.md)
- **Next action:** Create `synkage/skills/base_skill.py` (stateless `BaseSkill` with `name`, typed input/output models, `run()`) and a skill registry that rejects duplicate names (phase-03 ac-1). Then add permission gating: an agent may only call skills it's allowed to, otherwise `PermissionDenied` (ac-2).

## In progress
Nothing mid-flight. Phases 0–2 are done.

## Blockers
None for ac-1/ac-2. Before building **summarize** or **draft message**, open question 1 (LLM or not) needs an answer. **classify intent**, **plan steps** and **format note** can be rule-based, which is enough for ac-3 (3 of 5 skills).

## Open questions / unknowns
Do not guess these — ask the user when the phase that needs them starts.
1. **LLM or not (blocks Phase 3 text skills):** do summarize/draft/classify skills call an LLM (which provider?) or stay rule-based? Spec only says "no heavy model dependency required".
2. **Target OS (Phase 5):** Sticky Notes is Windows-only. Which OS is primary, and what's the note target on Linux/macOS?
3. **Browser sessions (Phase 5):** how WhatsApp Web / Gmail logins persist for Playwright. Involves credentials → needs a human.
4. **Memory location (Phase 7):** spec says repo `memory/`; personal data probably belongs in a user data dir (e.g. `~/.synkage/`). Same question for agent artifacts in `runs/`: they hold message text and are never cleaned up.
5. **Trust score (Phases 6–7):** how it's computed and what moves it.
6. **OpenClaw API (Phase 8):** no contract in the spec.
7. **Hotkeys / voice stub:** listed in `docs/proj.md` but not in any phase.

## Recent evidence
- `python -m pytest -q` → 140 passed.
- `python scripts/run_synkage.py prepare "send message to Raj: running late"` → planner → builder → reporter; report "Ready: send message to Raj via WhatsApp Web. Needs your confirmation."; artifacts in `runs/<run-id>/`.
- `tests/test_layer_boundaries.py` fails when an agent imports `synkage.execution` (checked by temporarily adding that import).
- ruff clean; OKF lint 0 errors; `phases_status.py` → current phase phase-03-skills.
