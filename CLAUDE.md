# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current state

**Design-only repo.** There is no source code yet — only `README.md`, `docs/`, `requirements.txt`, and `LICENSE`. The layout and file names below are the *planned* design from `docs/proj.md` and `docs/plan.md`; create them as work progresses rather than assuming they exist.

Build order follows `docs/plan.md` (Phase 0 → 9). Current target is **Phase 0**: folder structure, config loader, CLI entry `scripts/run_synkage.py`, basic logging, and a `tool_registry.json` schema. Exit criterion: the CLI starts, loads config, and prints the system state.

## Commands

Python 3.10+.

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
playwright install                 # required for browser automation; pip alone is not enough

python scripts/run_synkage.py      # CLI entry point (planned)
pytest                             # tests live in tests/ (pytest + pytest-asyncio)
pytest tests/test_x.py::test_name  # single test
```

No linter or formatter is configured yet.

## Planned stack (from requirements.txt)

typer + prompt-toolkit (CLI), rich (output), pydantic v2 (data contracts), pyyaml / python-dotenv (config), anyio + tenacity (async + retries), playwright (browser automation; selenium is the alternative), httpx (adapters), apscheduler (night cycle), watchdog (context signals), rapidfuzz (fuzzy command/alias matching), orjson.

## Architecture

Synkage is an **action-first execution copilot**, not a chatbot. Goal: understand a short command → pick a tool → execute safely → report briefly.

Pipeline:

```
interfaces → context → brain → agents → skills → execution (routing) → adapters → tools/runtimes → brain/verifier → report
```

### Layer boundaries (key invariants)

The design depends on each layer staying inside its own job. Keep these when writing code:

| Layer | Dir | Owns | Must NOT |
|---|---|---|---|
| Interface | `interfaces/` | Input/output, triggering confirmation prompts | Contain decision logic |
| Context | `context/` | Structured signals (activity, app, time) | Decide anything |
| Brain | `brain/` | Intent resolution, situation classification, autonomy level, strategy choice, delegation, verification | **Execute tools directly** |
| Agents | `agents/` | Specialist reasoning (planner, researcher, builder, critic, reporter); chain through **files** | Control tools directly |
| Skills | `skills/` | Atomic, **stateless**, permission-gated capabilities, called only by agents | Make decisions |
| Execution | `execution/` | Map task → adapter, **enforce autonomy policy**, confirmation loop, rollback | — |
| Adapters | `adapters/` | Translate tasks into backend calls; normalize results (`tool_adapter_base.py`, `local_exec_adapter.py`, `openclaw_adapter.py`) | Bypass the autonomy guard |
| Tools | `tools/` | Browser/desktop controllers doing real actions | Contain decision logic |
| Avatar | `avatar/` | Presentation only (future; locked until MVP is stable) | Decide or execute anything |

External runtimes such as **OpenClaw** are execution substrates only. Synkage keeps control of intent, autonomy, and safety. Every result goes back through the verifier.

### Situation awareness

Situation states come from **rules applied to signals, not from a model**: Idle / Normal / Focused / Urgent / Emergency. The state changes autonomy thresholds, how much confirmation is needed, and when Synkage may interrupt.

### Autonomy and safety (`docs/autonomy_safety.md`)

- Levels: **0** observe · **1** plan only · **2** execute with confirmation (**default**) · **3** limited auto-execute.
- The level is derived from intent confidence, situation state, task risk class, tool sensitivity, and user trust score.
- Risk classes: Low (notes, summaries) · Medium (messages, replies) · High (account actions, purchases) · Critical (financial, security, deletion). **High and Critical always need confirmation.**
- **Never autonomous:** payments, account changes, password handling, public posting, destructive file operations, system config changes.
- Confirmation loop: show plan → show tool target → require explicit confirm → execute → log.
- Audit log records for every execution: intent, tool, autonomy level, confirmation state, result.

### Command grammar (`docs/command_grammar.md`)

`<action> <object> [target] [options]`, e.g. `send whatsapp message to Raj: I'll call in 10 minutes`.
- Verbs: send, reply, create, save, open, find, summarize, plan, generate, execute.
- Tool directives: `use browser|gmail|whatsapp|vscode|sticky notes`.
- Autonomy modifiers: `preview only`, `ask before send`, `auto execute`, `dry run`.
- Agent directives: `research then write`, `plan then execute`, `chain agents`.
- **If the tool or target is unclear, switch to preview mode** — never guess and execute.

### Memory

File-based and local-first (`memory/`): `user_profile.json`, `relationship_state.json`, `logs.json`, `project.md`. A night cycle (`memory/night_cycle.py`, `scripts/nightly_update.py`) compresses logs, promotes patterns, adjusts trust, and applies behavior decay. Config lives in YAML under `config/` (`permissions.yaml`, `autonomy_levels.yaml`, `command_aliases.yaml`, `app_preferences.yaml`).

## Scope guardrails

- **MVP** (`docs/mvp_vs_phase2.md`, `docs/plan.md`): CLI, intent resolution, agent delegation, skills, tool routing, a message-draft flow (WhatsApp Web / Gmail) with confirmation, note saving, autonomy guard.
- **Do not add early:** voice, vision, continuous listening, avatar/3D UI, emotion modeling, autonomous financial actions. The avatar layer is locked until the MVP is stable.
- Keep it CPU-friendly with no heavy model dependency, and prefer delegating to existing tools over reinventing them.

## Known doc inconsistencies

- `tool_registry.json`: the README puts it in `config/`, but `docs/proj.md` puts it in `tools/`. Pick one when implementing and update the other doc.
- The README uses `cd synkage-core`, but the repo/clone directory is `synkage-os`.
