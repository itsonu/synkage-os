# Current state — Synkage Core

_Rewritten at the end of every session. This is the cold-start resume point._

- **Project status:** in_progress
- **Active phase:** phase-05-tool-control (in_progress, 1/5, **waiting on the user**) — see [phase file](../phases/phase-05-tool-control.md). Phases 6 and 7 were completed meanwhile.
- **Next action:** **Waiting on the user** to run [the Phase 5 manual checks](../okf/runbooks/phase5-manual-checks.md) on their Mac. Nothing else is buildable: Phase 8 is **deferred** (user, 2026-09-25) and Phase 9 (avatar) is locked until the MVP (Phases 1–5) is done.

## In progress
Phase 5 (waiting on the user). Phases 6 and 7 are done.

## Blockers
- **User's manual run** (their accounts, their Mac): needed for ac-2, ac-3 and ac-4. Never do it unattended (CLAUDE.md guardrails).
- **Selectors are unverified** against live WhatsApp Web and Gmail; expect a fix-up round after the first manual run.
- Phase 8: deferred by the user. Phase 9: locked until Phase 5 is done.

## Open questions / unknowns
Do not guess these — ask the user when the phase that needs them starts.
1. **LLM or not (blocks the deferred summarize + draft_message skills):** should they call an LLM (which provider?) or stay rule-based? Spec only says "no heavy model dependency required". Phase 3 shipped without them.
2. ~~Target OS~~ — answered: **macOS**. Notes go to Apple Notes (inferred; ADR-0008). Say if you prefer another app.
3. ~~Browser sessions~~ — decided: a persistent Chromium profile at `~/.synkage/browser-profile` (outside the repo). The user signs in with `synkage login`.
4. ~~Memory location~~ — answered: `~/.synkage/memory` (ADR-0010). Still open: `runs/` (agent artifacts, message text) stays in the repo folder, gitignored, with no cleanup.
5. ~~Trust score~~ — answered: confirmed success +, declined/failed −, daily decay toward neutral (ADR-0010). Open: whether and how trust should affect autonomy (it never may loosen hard rules).
6. ~~OpenClaw API~~ — moot for now: Phase 8 deferred by the user. Revisit if OpenClaw's API docs turn up.
7. **Hotkeys / voice stub:** listed in `docs/proj.md` but not in any phase.

## Recent evidence
- `python -m pytest -q` → 376 passed, 1 skipped.
- `python scripts/nightly_update.py` → `night cycle: trust 0.500 -> 0.500 (outcomes none); compressed 0 record(s), kept 0`, exit 0.
- Race test (appender thread vs 20 night cycles) passes; with the lock disabled it fails 5/5.
- ruff clean; OKF lint 0 errors; `phases_status.py` → phases 0–4, 6, 7 done; 5 in_progress 1/5; 8 deferred.
