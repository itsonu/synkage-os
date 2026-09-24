# Session log — Synkage Core

Append-only, newest first. One entry per working session: what changed, what was decided, what's next.

---

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
