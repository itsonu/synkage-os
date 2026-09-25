# Current state — Synkage Core

_Rewritten at the end of every session. This is the cold-start resume point._

- **Project status:** in_progress
- **Active phase:** phase-05-tool-control (in_progress, 1/5, **waiting on the user**) — see [phase file](../phases/phase-05-tool-control.md). Phase 6 was completed meanwhile.
- **Next action:** **Waiting on the user** to run [the Phase 5 manual checks](../okf/runbooks/phase5-manual-checks.md) on their Mac and report pass/fail per step. Meanwhile, Phase 7 (memory & night cycle) is unblocked, but it needs open question 4 (memory location) answered first.

## In progress
Phase 5 (waiting on the user). Phase 6 is done.

## Blockers
- **User's manual run** (their accounts, their Mac): needed for ac-2, ac-3 and ac-4. Never do it unattended (CLAUDE.md guardrails).
- **Selectors are unverified** against live WhatsApp Web and Gmail; expect a fix-up round after the first manual run.
- Phase 7 depends only on Phase 4. It can proceed once open question 4 (memory location) is answered.

## Open questions / unknowns
Do not guess these — ask the user when the phase that needs them starts.
1. **LLM or not (blocks the deferred summarize + draft_message skills):** should they call an LLM (which provider?) or stay rule-based? Spec only says "no heavy model dependency required". Phase 3 shipped without them.
2. ~~Target OS~~ — answered: **macOS**. Notes go to Apple Notes (inferred; ADR-0008). Say if you prefer another app.
3. ~~Browser sessions~~ — decided: a persistent Chromium profile at `~/.synkage/browser-profile` (outside the repo). The user signs in with `synkage login`.
4. **Memory location (Phase 7):** spec says repo `memory/`; personal data probably belongs in a user data dir (e.g. `~/.synkage/`). Same question for agent artifacts in `runs/`: they hold message text and are never cleaned up.
5. **Trust score (Phase 7):** how it's computed and what moves it. (Phase 6 didn't need it.)
6. **OpenClaw API (Phase 8):** no contract in the spec.
7. **Hotkeys / voice stub:** listed in `docs/proj.md` but not in any phase.

## Recent evidence
- `python -m pytest -q` → 346 passed, 1 skipped.
- `python scripts/run_synkage.py status` → `Situation: normal (no rule matched)`; `--situation focused run "save note meeting at 4pm"` runs without a confirmation prompt, while `--situation idle` asks.
- ruff clean; OKF lint 0 errors; `phases_status.py` → phase-06 done, phase-05 in_progress 1/5.
