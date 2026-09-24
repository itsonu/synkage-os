# Spec — Synkage Core

The spec is the existing design docs, kept as-is (not copied here, to avoid two versions drifting):

| Doc | Covers |
|---|---|
| [README.md](../README.md) | Product definition, capabilities, MVP scope, autonomy table, command examples |
| [architecture.md](architecture.md) | Layers and their boundaries, situation model, strategy selection, memory, external runtimes |
| [autonomy_safety.md](autonomy_safety.md) | Autonomy levels, risk classes, hard safety rules, confirmation loop, audit fields |
| [command_grammar.md](command_grammar.md) | Command format, verbs, directives, modifiers |
| [plan.md](plan.md) | Phase 0–9 build plan and MVP definition (source of `docs/phases/`) |
| [mvp_vs_phase2.md](mvp_vs_phase2.md) | MVP / Phase-2 / Phase-3 scope |
| [proj.md](proj.md) | Intended file layout (see ADR-0006 for where code actually lives) |
| [research_abstract.md](research_abstract.md) | One-paragraph summary |

Where the implementation deviates from these, an ADR in [okf/decisions/](okf/decisions/index.md) says why.
