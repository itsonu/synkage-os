# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> Operating contract for any coding agent working this repo. **Read this first, every session.**

## What this is
Synkage Core is a situation-aware, **action-first** execution copilot, not a chatbot. It takes a short command, picks a tool, runs it within autonomy limits, and reports back briefly.

Spec: [docs/SPEC.md](docs/SPEC.md) (an index of the design docs in `docs/`).

## Navigation
- **Where am I / what's next:** [docs/context/state.md](docs/context/state.md). Always resume from here.
- **Roadmap & progress:** [docs/phases/index.md](docs/phases/index.md). Machine state is in `docs/phases/phases.json`, which is the source of truth.
- **How the system fits together:** [docs/okf/index.md](docs/okf/index.md), the OKF knowledge graph. Check it before changing code.
- **Why decisions were made:** [docs/okf/decisions/](docs/okf/decisions/index.md) (ADRs).
- **Running memory:** [docs/context/session-log.md](docs/context/session-log.md).

## Tech stack
Python 3.10+. typer + prompt-toolkit (CLI), rich (output and logging), pydantic v2 (all data contracts and config validation), pyyaml + python-dotenv (config), anyio + tenacity (async, retries), playwright (browser automation, [ADR-0007](docs/okf/decisions/0007-playwright-browser-automation.md)), httpx (adapters), apscheduler (night cycle), watchdog (context signals), rapidfuzz (fuzzy matching). Dependencies are listed in `requirements.txt`. `pyproject.toml` holds tool config only (pytest, ruff).

## Commands
```bash
pip install -r requirements.txt ruff       # setup (inside a venv)
playwright install                         # browser binaries; needed from Phase 5
python scripts/run_synkage.py              # run: load config, print system state (= python -m synkage)
python scripts/run_synkage.py --log-level DEBUG --config-dir path/to/config status
python scripts/run_synkage.py parse "send message to Rahul" [--json]   # intent + autonomy decision
python scripts/run_synkage.py prepare "send message to Raj: late"      # + agent chain -> report, artifacts in runs/
python scripts/run_synkage.py run "send message to Raj dry run: hi"    # parse -> prepare -> confirm -> route (+audit)
python scripts/run_synkage.py shell        # interactive `run` loop
python scripts/run_synkage.py skills       # registered skills + which agents may call them
python -m pytest -q                        # all tests
python -m pytest tests/test_config.py::test_cannot_drop_hard_safety_rule   # single test
ruff check . && ruff format --check .      # lint + format check
python scripts/gen_schema.py               # after editing Tool/ToolRegistry models
python docs/okf/.tools/okf_lint.py --repo . --bundle docs/okf   # OKF lint (0 errors required)
python scripts/phases_status.py            # phase board + next action
```
Use `python -m pytest`, not bare `pytest`. A globally installed pytest may run under a different interpreter that lacks the project's dependencies.

CI (`.github/workflows/ci.yml`) runs ruff, pytest, the CLI boot, OKF lint, and the phase board.

## Architecture

Pipeline: `interfaces → context → brain → agents → skills → execution → adapters → tools → brain verifier → report`.

### Layout ([ADR-0006](docs/okf/decisions/0006-package-layout.md))
- Code lives in the `synkage/` package, one subpackage per layer: `synkage/{brain,agents,skills,execution,adapters,tools,context,memory,avatar,interfaces}`. This differs from the flat top-level folders shown in README and `docs/proj.md`.
- Runtime config lives in root `config/`, including `tool_registry.json`.
- `synkage/config.py` loads and validates every file in `config/` into one typed `SynkageConfig`. Any failure raises `ConfigError`, and the CLI exits 1.
- `synkage/interfaces/cli.py` is the Typer app. Its callback loads config for every command and puts it on `ctx.obj`.
- Command flow today: `Prime.handle(text)` (`synkage/brain/prime.py`) → `IntentResolver.resolve` → `Intent` → `AutonomyGuard.decide` → `AutonomyDecision`. `Prime.delegate(result)` then runs an agent chain (planner → builder → reporter, or planner → reporter for previews). Agents communicate **only through JSON artifact files** in `runs/<run-id>/NN-<agent>.json` (gitignored; `SYNKAGE_RUNS_DIR` overrides; tests use a temp dir). Finally `execution/autonomy_router.AutonomyRouter.route(request, intent, decision, confirmation)` is the **only** place an action may run. It loads the builder's draft as an `ActionRequest`, re-derives risk and safety categories itself (never trusting the decision), refuses anything unconfirmed that needs confirmation, never calls the adapter on a dry run, takes the adapter from the tool's registry entry, and appends every outcome to the audit log (`logs.jsonl`, gitignored; `SYNKAGE_AUDIT_LOG` overrides; tests use a temp file). The interface layer injects `ask`/`show` into `confirm()` so the rule stays out of the UI.
- Adapters subclass `ToolAdapter` and register in `synkage/adapters/registry.py`. Tool controllers register in `local_exec_adapter.CONTROLLERS[tool_id]`. All seeded tools are `enabled: false`, so real commands end `unavailable` until Phase 5.
- New agents subclass `BaseAgent` (`name`, `kind`, `produce()`) and register in `synkage/agents/registry.py`. `run()` turns every failure into `status=failed`; it never raises.
- Agents reach skills **only** via `self.skills.call(name, **data)`, a registry client bound to the agent's name. `SkillRegistry.invoke` checks `agent_skills` in `config/permissions.yaml` (default deny) before validating input, and builds a fresh skill instance per call. New skills subclass `BaseSkill` (`name`, `description`, `Input`, `Output`, `run()`), live in `synkage/skills/{text,analysis,decision}/`, and are added to `DEFAULT_SKILLS` and to an agent's `agent_skills` entry.
- `tests/test_layer_boundaries.py` enforces the import rules below. Extend it when a new layer gets code.

### Layer boundaries (invariants — keep them)
| Layer | Owns | Must NOT |
|---|---|---|
| interfaces | Input/output, confirmation prompts | Contain decision logic |
| context | Structured signals (activity, app, time) | Decide anything |
| brain | Intent, situation, autonomy level, strategy, delegation, verification | **Execute tools directly** |
| agents | Specialist reasoning; chain work through **files** | Control tools directly |
| skills | Atomic, **stateless**, permission-gated capabilities; called only by agents | Make decisions |
| execution | Task → adapter mapping, **autonomy enforcement**, confirmation loop, rollback, audit log | — |
| adapters | Translate tasks into backend calls; normalize results | Bypass the autonomy guard |
| tools | Real browser/desktop actions | Contain decision logic |
| avatar | Presentation only; **locked until MVP is stable** | Decide or execute |

External runtimes such as OpenClaw are reached only through adapters and remain under the autonomy guard ([ADR-0005](docs/okf/decisions/0005-external-runtimes-as-adapters.md)).

### Autonomy & safety ([ADR-0002](docs/okf/decisions/0002-bounded-autonomy.md), `docs/autonomy_safety.md`)
- Levels: 0 observe · 1 plan · **2 confirm (default)** · 3 limited auto.
- Risk classes are low, medium, high and critical. **High and critical always need confirmation.**
- **Never autonomous:** payments, account changes, password handling, public posting, destructive file operations, system config changes. These are hard-coded in `HARD_NEVER_AUTONOMOUS`. The config loader rejects any config that drops one or relaxes high/critical risk, so config can tighten the rules but never loosen them.
- Confirmation loop: show the plan → show the tool target → get an explicit confirm → execute → log. Audit fields are intent, tool, autonomy level, confirmation state and result.
- **If the tool or target is unclear, switch to preview mode.** Never guess and then execute.
- Situation detection uses rules over signals, not a model ([ADR-0003](docs/okf/decisions/0003-rule-based-situation-detection.md)).

### Command grammar (`docs/command_grammar.md`)
`<action> <object> [target] [options]`, with message content after the first `:`. Options go **before** the `:`. Options inside content never apply, but a safer one (`dry run`, `preview only`, `ask before send`) at the end of the content forces preview. The vocabulary lives in `config/command_aliases.yaml`: per-verb `needs_target`/`needs_tool` rules, object noun → task type, `use <tool>` directives, autonomy modifiers and agent directives. Tools resolve in this order: `use X` directive > inline mention > preferred tool for the object's task type. Safety categories are matched by whole-word keywords in `config/permissions.yaml`.

## How to work this repo (autonomy loop)
1. Read this file, then `docs/context/state.md` to find the active phase and the next action.
2. Open the active phase in `docs/phases/` and load its acceptance criteria. They define done for now. Stay in scope.
3. Check the OKF graph for the concepts the phase touches. Read the real source before changing it.
4. Do the next action, one change-set at a time.
5. Update the OKF concept for every file you change (body and `timestamp`). When a `planned` concept's file comes into existence, add `sources:` and set its `## Status`. OKF lint must report 0 errors.
6. Tick acceptance criteria in `phases.json` **with concrete evidence** (a test name, command output, a file or a commit), and mirror the tick in the phase `.md`. No evidence means the criterion is not met.
7. Append to `session-log.md` and rewrite `state.md` so the next session can resume cleanly.
8. Commit with a conventional-commit message. Keep commits small and coherent.
9. When all of a phase's criteria are met, advance `current_phase` and repeat. MVP is reached when Phases 1–5 are done.

## Conventions
- **Read before write; audit before fix.**
- **Conventional commits** (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`).
- **No "done" without evidence.**
- **Keep trackers truthful.** `state.md` and `phases.json` must always reflect reality.
- **Surface unknowns.** Open questions are listed in `state.md`. Ask when a phase needs one answered; don't guess.
- **Scope guardrails:** don't add voice, vision, continuous listening, avatar/3D UI, emotion modeling or autonomous financial actions early. Keep it CPU-friendly and prefer existing tools over reinventing them.
- New config files or fields go through a pydantic model in `synkage/config.py` (`extra="forbid"`) plus a test. For registry model changes, regenerate the schema.

## Guardrails — stop and ask a human before:
- Entering or committing secrets, credentials, API keys, tokens, or browser login sessions.
- Irreversible destruction (force-push, history rewrite, deleting user data).
- Sending or publishing as the user (real WhatsApp or Gmail sends, posts), or pushing to shared/protected branches without a go-ahead.
- Deploying to production, changing infra/billing/account settings, or spending money.

## Definition of done (project)
Every phase in `phases.json` is `done`, with all acceptance criteria met and evidenced. The OKF bundle lints with 0 errors, and `state.md` reads `project: complete`. Phase 8 (optional) and Phase 9 (locked) may be explicitly deferred by the user.
