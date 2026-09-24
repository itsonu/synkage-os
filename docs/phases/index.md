# Roadmap — Synkage Core

Machine state: [`phases.json`](phases.json) (source of truth). Board: `python scripts/phases_status.py`.
Numbering follows `docs/plan.md`. **MVP = Phases 1–5 done.** Phases 6–7 can run in parallel after 4; 8 is optional; 9 is locked.

| # | Phase | Status | Criteria | Depends on |
|---|---|---|---|---|
| [00](phase-00-foundation.md) | Foundation | done | 8/8 | — |
| [01](phase-01-brain.md) | Brain layer | done | 6/6 | 00 |
| [02](phase-02-agents.md) | Agent layer | done | 4/4 | 01 |
| [03](phase-03-skills.md) | Skills system | todo | 0/4 | 02 |
| [04](phase-04-routing.md) | Execution routing | todo | 0/5 | 03 |
| [05](phase-05-tool-control.md) | Tool control | todo | 0/5 | 04 |
| [06](phase-06-situation.md) | Situation awareness | todo | 0/4 | 04 |
| [07](phase-07-memory.md) | Memory & night cycle | todo | 0/4 | 04 |
| [08](phase-08-openclaw.md) | OpenClaw integration (optional) | todo | 0/3 | 04 |
| [09](phase-09-avatar.md) | Avatar layer (locked) | todo | 0/3 | 05, 06, 07 |

Current phase: **phase-03-skills**. Resume point: [state.md](../context/state.md).
